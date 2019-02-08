#!/usr/bin/env python
"""RabbitMQ message worker for vCloud Director Extensibility SDK.
"""

import base64
import sys
import json
import logging
import importlib
from kombu import Exchange, Queue, Connection
from kombu.mixins import ConsumerMixin
from kombu.utils.debug import setup_logging


# name the worker for the module
logger = logging.getLogger("VcdExtMessageWorker")


class MessageWorker(ConsumerMixin):
    """kombu.ConsumerMixin based object.

    A kombu.ConsumerMixin based object that handle the messages
    received in the RabbitMQ queue and process them. When proceed,
    an reply is sent back.
    """

    def __init__(self, connection, exchange, queue, routing_key,
                sub_worker, thread_support=True, no_declare=True):
        """Init a new ConsumerMixin object.

        Args:
            connection (kombu.Connection): The Kombu Connection object context.
            exchange (str): The Exchange to use on RabbitMQ.
            queue (str): The listen queue to use on RabbitMQ.
            routing_key (str): The routing key to use on RabbitMQ.
            sub_worker (str): Name of subworker as a string: ex: `package.module.className`.
            thread_support (bool, optional): Defaults to True. Does the worker support Thread behavior?
            no_declare (bool, optional): Defaults to True. Declare Exchange and Queue when connecting?
        """
        # Reduce logging from amqp module
        setup_logging(loglevel='INFO', loggers=['amqp'])
        logger.debug(f"Initializating a new listener for exchange/queue: {exchange}/{queue}...")
        self.connection = connection
        self.exchange = Exchange(exchange, 'direct',
                                durable=True, no_declare=no_declare)
        self.queue = Queue(queue, exchange=self.exchange,
                            routing_key=routing_key, no_declare=no_declare)
        self.queues = [self.queue]
        self.no_declare = no_declare
        logger.info(f"New listener initialized for exchange/queue: {exchange}/{queue}...")
        logger.debug(f"Importing sub_worker module: {sub_worker}...")
        self.sub_worker = sub_worker
        self.thread_support = thread_support
        mod_name = '.'.join(self.sub_worker.split(".")[:-1])
        try:
            self.sub_worker_mod = importlib.import_module(mod_name)
        except ModuleNotFoundError as e:
            logger.error(f"Cannot import the sub worker module named {mod_name}: ModuleNotFoundError")
            sys.exit(-1)
        except Exception as e:
            logger.error(f"Cannot import the sub worker module named {mod_name}: " + str(e))
            sys.exit(-1)

    def get_consumers(self, Consumer, channel):
        """Return the consumer objects.

        Args:
            Consumer (kombu..messaging.Consumer): Current consumer object.
            channel (str): Incoming channel for messages (unused).

        Returns:
            kombu..messaging.Consumer: A Consumer message with callback to local task.
        """
        logger.debug("Get worker consumers")
        return [Consumer(
            queues=self.queues,
            callbacks=[self.process_task]
        )]

    def process_task(self, body, message):
        """Process a single message on receive.

        Args:
            body (str): JSON message body as a string.
            message (str): JSON message metadata as a string.
        """
        logger.info("Listener: New message received in MQ")
        try:
            json_payload = json.loads(body)
        except ValueError:
            logger.error("Listener: Invalid JSON data received: ignoring the message\n{body}")
            return
        try:
            message.ack()
        except ConnectionResetError:
            logger.error("Listener: ConnectionResetError: message may have not been ack...")
        message.properties['id'] = json_payload[0]['id']
        logger.debug("Listener: Processing request message in a new thread...")
        try:
            if self.thread_support:
                thread = getattr(
                    self.sub_worker_mod,
                    self.sub_worker.split(".")[-1])(
                        message_worker = self,
                        data = json_payload,
                        message = message
                    )
                thread.start() # threading usage
            else:
                pass # not yet implemented
        except Exception as exc:
            logger.error('Listener: Task raised exception: %r', exc)

    def publish(self, data, properties):
        """Publish a message through the current connection.

        Args:
            data (str): JSON message body as a string.
            properties (str): JSON message metadata as a string.
        """
        logger.debug("Publisher: Sending a message to MQ...")
        rqueue = Queue(
            properties['reply_to'],
            Exchange(
                properties["replyToExchange"], 'direct',
                durable=True, no_declare=self.no_declare),
            routing_key=properties['reply_to'],
            no_declare=self.no_declare
        )
        if properties.get("encode", True):
            rsp_body = (base64.b64encode(data.encode('utf-8'))).decode()
        else:
            rsp_body = (base64.b64encode(data)).decode() # raw data
        rsp_msg = {
            'id': properties.get('id', None),
            'headers': {
                'Content-Type': properties.get(
                    "Content-Type", "application/*+json;version=31.0" # default
                ),
                'Content-Length': len(data)
            },
            'statusCode': properties.get("statusCode", 200),
            'body': rsp_body
        }
        try:
            self.connection.Producer().publish(
                rsp_msg,
                correlation_id=properties['correlation_id'],
                routing_key=rqueue.routing_key,
                exchange=rqueue.exchange,
                retry = True,
                expiration = 10000
            )
            logger.info("Publisher: Response sent to MQ")
        except ConnectionResetError:
            logger.error("Publisher: ConnectionResetError: message may be not sent...")
