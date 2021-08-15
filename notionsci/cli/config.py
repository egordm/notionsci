import click

from notionsci.config import config as conf


@click.command()
def config():
    """
    Prints current config file as is
    """
    print(conf.dumps_yaml())
