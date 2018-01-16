import click
import json
import logging
import stevedore.extension

LOG = logging.getLogger(__name__)
MGR = stevedore.extension.ExtensionManager('sparkle.cmd')


class Sparkle():
    def __init__(self):
        self.config = {}

    def configure(self, config):
        self.config.update(config)


@click.group()
@click.option('--quiet', 'loglevel',
              flag_value='WARNING', default=True)
@click.option('--verbose', '-v', 'loglevel',
              flag_value='INFO')
@click.option('--debug', '-d', 'loglevel',
              flag_value='DEBUG')
@click.option('--config', '-f', 'configfiles',
              type=click.File(), multiple=True)
@click.pass_context
def cli(ctx, loglevel=None, configfiles=None):
    logging.basicConfig(level=loglevel)
    app = Sparkle()
    ctx.obj = app
    ctx.auto_envvar_prefix = 'SPARKLE'

    for cfg in configfiles:
        app.configure(json.load(cfg))


@cli.command()
@click.pass_context
def dumpconfig(ctx):
    app = ctx.obj
    print(json.dumps(app.config, indent=2))


for command in MGR.extensions:
    cli.add_command(command.plugin, name=command.name)
