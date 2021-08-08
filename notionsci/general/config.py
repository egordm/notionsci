import click
from notionsci.config import config as conf

@click.command()
def config():
    print(conf.dumps_yaml())