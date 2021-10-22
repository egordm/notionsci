import click

from notionsci.config import config
from notionsci.connections.notion import parse_uuid_callback, ID
from notionsci.sync.markdown import MarkdownPagesSync


@click.group()
def markdown():
    """
    Collection of Sync commands for Markdown documents
    """
    pass


@markdown.command()
@click.argument('collection', callback=parse_uuid_callback, required=True)
@click.argument('dir', required=True)
@click.option('--force', is_flag=True, default=False,
              help='Ensures up to date items are also pushed to Zotero')
def pages(collection: ID, dir: str, force: bool):
    """
    Starts a sync of a collection to a folder of markdown files

    COLLECTION: Database ID or url
    DIR: Directory path to sync to
    """
    notion = config.connections.notion.client()

    MarkdownPagesSync(notion, collection, dir).sync()