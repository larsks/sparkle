import click
import json
import logging

from sparkle import client
from sparkle import defaults

LOG = logging.getLogger(__name__)


@click.command()
@click.option('--broker-uri', '-b', type=int)
@click.option('--subscribe', '-s', 'subscriptions', multiple=True)
@click.pass_context
def command(ctx, broker_uri, subscriptions):
    app = ctx.obj

    if not subscriptions:
        subscriptions = ('',)

    broker_uri = broker_uri or app.config.get('broker_pub_uri',
                                              defaults.broker_pub_uri)

    broker = client.Client(broker_pub_uri=broker_uri)
    for sub in subscriptions:
        broker.subscribe(sub)

    for topic, data in broker.messages():
        print(topic, json.dumps(data))
