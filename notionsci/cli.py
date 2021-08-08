import logging

import click

import notionsci.general.config
from notionsci import sync


@click.group()
@click.option("-v", "--verbose", count=True)
def cli(verbose):
    logging.basicConfig(level=logging.DEBUG if verbose > 0 else logging.INFO)


cli.add_command(sync.sync)
cli.add_command(notionsci.general.config.config)
