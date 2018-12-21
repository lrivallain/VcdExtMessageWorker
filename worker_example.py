#!/usr/bin/env python
""" This is an example of a threaded worker that can be
        executed from a VcdExtMessageWorker instance

    The example shows how to retrieve some informations
        from the message sent by vCD.
"""


import base64
import json
import logging
from threading import Thread

# name the worker for the module
logger = logging.getLogger(__name__)


class SampleWorker(Thread):
    def __init__(self, message_worker, data, message):
        Thread.__init__(self)
        # enable to publish response from the worker
        self.message_worker = message_worker
        # content of the request message
        self.data = data
        # message metadata
        self.message = message


    def run(self):
        """ Function to handle all messages received on the RabbitMQ Exchange
        """
        # split request content from vcd context data
        req_data = self.data[0]
        vcd_data = self.data[1]
        # parse information from request
        org_id = vcd_data.get('org', '').split("urn:vcloud:org:")[1]
        user_id = vcd_data.get('user', '').split("urn:vcloud:user:")[1]
        method = req_data.get('method', None)
        query_string = req_data.get('queryString', None)
        # log the request as a web server standart for legal usage
        remote_addr = req_data.get('remoteAddr', None)
        remote_port = req_data.get('remotePort', None)
        remote_protocol = req_data.get('protocol', None)
        request_uri = req_data.get('requestUri', None)
        data = base64.b64decode(req_data.get('body', ''))
        req_uri = req_data.get('requestUri', None)
        # do whatever you need to do to proceed message and get a message to return
        rsp_body = {
            "something": "value of something"
        }
        # prepare answer properties
        resp_prop = {
            "id": req_data['id'],
            "accept": req_data['headers'].get('Accept', None),
            "correlation_id": self.message.properties['correlation_id'],
            "reply_to": self.message.properties['reply_to'],
            "replyToExchange": self.message.headers['replyToExchange']
        }
        # end by sending the message
        self.message_worker.publish(json.dumps(rsp_body, indent=4), resp_prop)
        # do more? (async for example)
        return