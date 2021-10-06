import click

from .zotero import zotero
from .markdown import markdown


@click.group()
def sync():
    """
    Collection of Sync commands for various services
    """
    pass


sync.add_command(zotero)
sync.add_command(markdown)
