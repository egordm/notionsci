import click

from .zotero import zotero


@click.group()
def sync():
    pass


sync.add_command(zotero)
