import click
import json
import logging
import os
import select

from sparkle import client
from sparkle import defaults

LOG = logging.getLogger(__name__)


@click.command()
@click.option('--broker-uri', '-b', type=int)
@click.argument('fifopath')
@click.pass_context
def command(ctx, broker_uri, fifopath):
    '''Read messages on a local fifo and send them to the broker.

    The startup time for a Python script on the Raspberry Pi can be
    significant. Rather than spinning up the send-message command,
    this script creates the named FIFO and then reads from it messages
    of the form `<topic>\n<data>`, where `<data>` is JSON-encoded
    content, and then sends the message to the broker.
    '''

    app = ctx.obj

    broker_uri = broker_uri or app.config.get('broker_sub_uri',
                                              defaults.broker_sub_uri)

    broker = client.Client(broker_sub_uri=broker_uri)

    LOG.debug('creating fifo %s', fifopath)
    try:
        os.unlink(fifopath)
    except OSError:
        pass
    os.mkfifo(fifopath)

    while True:
        LOG.debug('opening fifo %s', fifopath)
        with open(fifopath, 'r') as fifo:
            data = fifo.read()

        try:
            marker = data.find('\n')
            topic = data[:marker]
            data = data[marker:]
            data = json.loads(data)
            broker.send_message(topic, data)
        except ValueError as e:
            LOG.error('failed to send message: %s', e)
