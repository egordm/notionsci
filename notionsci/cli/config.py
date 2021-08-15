import click

from notionsci.config import config as conf


@click.command()
@click.option('-f', '--file', required=False, help='File to dump config to')
def config(file):
    """
    Prints current config file as is
    """
    if file:
        with open(file, 'w') as f:
            f.write(conf.dumps_yaml())
    print(conf.dumps_yaml())
