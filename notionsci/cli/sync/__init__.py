import click

from .zotero import zotero


@click.group()
def sync():
    """
    Collection of Sync commands for various services
    """
    pass


sync.add_command(zotero)
