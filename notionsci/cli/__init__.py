import logging

import click

from notionsci.cli import config, notion, sync


@click.group()
@click.option("-v", "--verbose", count=True)
def cli(verbose):
    logging.basicConfig(level=logging.DEBUG if verbose > 0 else logging.INFO)


cli.add_command(sync.sync)
cli.add_command(config.config)
cli.add_command(notion.notion)
