import click
import logging
import time

from sparkle import client
from sparkle import defaults

LOG = logging.getLogger(__name__)


@click.command(name='send-message')
@click.option('--broker-uri', '-b', type=int)
@click.argument('topic')
@click.argument('kv', nargs=-1)
@click.pass_context
def command(ctx, broker_uri, topic, kv):
    app = ctx.obj

    broker_uri = broker_uri or app.config.get('broker_sub_uri',
                                              defaults.broker_sub_uri)

    broker = client.Client(broker_sub_uri=broker_uri)
    data = {k: v for k, v in [i.split('=', 1) for i in kv]}

    # give zmq time to establish connection
    time.sleep(0.1)

    broker.send_message(topic, data)
    broker.term()
