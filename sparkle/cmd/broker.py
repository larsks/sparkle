import click
import logging
import zmq

from sparkle import defaults

LOG = logging.getLogger(__name__)


@click.command()
@click.option('--pub-port', '-p', type=int)
@click.option('--sub-port', '-s', type=int)
@click.pass_context
def broker(ctx, pub_port, sub_port):
    app = ctx.obj

    pub_port = pub_port or app.config.get('broker_pub_port',
                                          defaults.broker_pub_port)
    sub_port = sub_port or app.config.get('broker_sub_port',
                                          defaults.broker_sub_port)

    zmqctx = zmq.Context()

    LOG.debug('creating broker pub socket on port %s', pub_port)
    pub = zmqctx.socket(zmq.PUB)
    pub.bind('tcp://127.0.0.1:%d' % pub_port)

    LOG.debug('creating broker sub socket on port %s', sub_port)
    sub = zmqctx.socket(zmq.SUB)
    sub.subscribe('')
    sub.bind('tcp://127.0.0.1:%d' % sub_port)

    LOG.info('starting broker')
    zmq.proxy(sub, pub)
