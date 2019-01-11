# VcdExtMessageWorker

VcdExtMessageWorker provides a way to handle, relay and answer to
RabbitMQ messages produced from the VMware vCloud Director extensibility
SDK (both for UI and API extension)

```python
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
```

## Installation

Get binaries (as ``.whl`` file), then run ``pip install`` as:

```bash
pip install VcdExtMessageWorker-<version>-py3-none-any.whl
```

Or from PIP:

```bash
pip install VcdExtMessageWorker
```

## Build and tests

```bash
python setup.py bdist_wheel && python -m pip install dist/VcdExtMessageWorker-<version>-py3-none-any.whl --force-reinstall
```