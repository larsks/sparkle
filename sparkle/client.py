import json
import logging
import zmq

LOG = logging.getLogger(__name__)


class Client():
    version = 1

    def __init__(self, broker_pub_uri=None, broker_sub_uri=None):
        self.broker_pub_uri = broker_pub_uri
        self.broker_sub_uri = broker_sub_uri
        self.pub = None
        self.sub = None

        self.init_zmq()

    def init_zmq(self):
        self.ctx = zmq.Context()

        if self.broker_sub_uri:
            LOG.debug('connecting to subscriber @ %s', self.broker_sub_uri)
            self.pub = self.ctx.socket(zmq.PUB)
            self.pub.connect(self.broker_sub_uri)

        if self.broker_pub_uri:
            LOG.debug('connecting to publisher @ %s', self.broker_pub_uri)
            self.sub = self.ctx.socket(zmq.SUB)
            self.sub.connect(self.broker_pub_uri)

    def send_message(self, topic, data):
        topic = 'sparkle.v{version}.{topic}'.format(
            version=self.version, topic=topic)
        LOG.debug('send on topic %s: %s', topic, data)
        self.pub.send_multipart((
            topic.encode('utf-8'), json.dumps(data).encode('utf-8')))

    def receive_message(self):
        topic, data = self.sub.recv_multipart()
        return (topic.decode('utf-8'),
                json.loads(data.decode('utf-8')))

    def messages(self):
        while True:
            topic, data = self.receive_message()
            yield (topic, data)

    def subscribe(self, subscription):
        LOG.debug('subscribing to %r', subscription)
        self.sub.subscribe(subscription)

    def term(self):
        if self.pub:
            self.pub.close()

        if self.sub:
            self.sub.close()

        self.ctx.term()
