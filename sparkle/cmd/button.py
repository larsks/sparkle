import click
import logging
import signal
import threading

import RPi.GPIO as GPIO

from sparkle import client
from sparkle import defaults
from sparkle import gpio_common  # NOQA

LOG = logging.getLogger(__name__)


class ButtonHandler(threading.Thread):
    def __init__(self, pin, func, edge=GPIO.BOTH, bouncetime=200):
        super().__init__(daemon=True)

        self.edge = edge
        self.func = func
        self.pin = pin
        self.bouncetime = float(bouncetime) / 1000

        self.lastpinval = GPIO.input(self.pin)
        self.lock = threading.Lock()

    def __call__(self, *args):
        if not self.lock.acquire(blocking=False):
            return

        t = threading.Timer(self.bouncetime, self.read, args=args)
        t.start()

    def read(self, *args):
        pinval = GPIO.input(self.pin)

        if (
                ((pinval == 0 and self.lastpinval == 1) and
                 (self.edge in [GPIO.FALLING, GPIO.BOTH])) or
                ((pinval == 1 and self.lastpinval == 0) and
                 (self.edge in [GPIO.RISING, GPIO.BOTH]))
        ):
            self.func(self.pin, pinval)

        self.lastpinval = pinval
        self.lock.release()


@click.command()
@click.option('--broker-uri', '-b', type=int)
@click.option('--name', '-n', required=True)
@click.option('--pin', '-p', type=int, required=True)
@click.option('--pull-up', '-U', 'pull',
              flag_value=GPIO.PUD_UP, default=True)
@click.option('--pull-down', '-D', 'pull',
              flag_value=GPIO.PUD_DOWN)
@click.option('--pull-none', '-N', 'pull',
              flag_value=GPIO.PUD_OFF)
@click.option('--active-high', '-H', 'active_high',
              flag_value=True, default=True)
@click.option('--active-low', '-L', 'active_high',
              flag_value=False)
@click.pass_context
def command(ctx, broker_uri, name, pin, pull, active_high):
    app = ctx.obj

    LOG.debug('button on pin %d active_high %s pull %d',
              pin, active_high, pull)

    broker_uri = broker_uri or app.config.get('broker_sub_uri',
                                              defaults.broker_sub_uri)

    broker = client.Client(broker_sub_uri=broker_uri)

    def button_callback(pin, value):
        if (value and active_high) or (not value and not active_high):
            topic = 'button.press'
        elif (not value and active_high) or (value and not active_high):
            topic = 'button.release'

        broker.send_message(topic, dict(name=name, value=value))

    GPIO.setup(pin, GPIO.IN, pull_up_down=pull)
    cb = ButtonHandler(pin, button_callback, edge=GPIO.BOTH, bouncetime=100)
    cb.start()
    GPIO.add_event_detect(pin, GPIO.BOTH, callback=cb)
    signal.pause()
