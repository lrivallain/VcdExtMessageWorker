===================
VcdExtMessageWorker
===================

VcdExtMessageWorker provides a way to handle, relay and answer to
RabbitMQ messages produced from the VMware vCloud Director extensibility
SDK (both for UI and API extension)

    #!/usr/bin/env python
    
    from vcdextmessageworker import MessageWorker, Connection
    with Connection(
        (f"amqp://{RABBIT_USER}:{RABBIT_PASSWORD}@{RABBIT_HOST}:5672/%2F"),
        heartbeat=4
    ) as conn:
        worker = MessageWorker(
            conn,
            exchange=RABBIT_EXCHANGE,
            queue=RABBIT_QUEUE,
            routing_key=RABBIT_ROUTINGKEY,
            sub_worker="worker_example.SampleWorker",
            thread_support=True
        )
        worker.run()


Installation
============

Get binaries (as ``.tgz`` file), then run ``pip install`` as:

    pip install dist/VcdExtMessageWorker-1.0.tar.gz


Build and tests
---------------

From the source code folder, create the distribution file and force reinstall:

    python setup.py sdist &&  pip install dist/VcdExtMessageWorker-1.0.tar.gz --force-reinstall

