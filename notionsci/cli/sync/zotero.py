import uuid

import click

from notionsci.cli.notion import duplicate
from notionsci.config import config
from notionsci.connections.notion import parse_uuid, parse_uuid_callback
from notionsci.connections.zotero import ID
from notionsci.sync.zotero import RefsOneWaySync, CollectionsOneWaySync


@click.group()
def zotero():
    """
    Collection of Sync commands for [Zotero](https://www.zotero.org/)
    """
    pass


# TODO: check if properties exist and throw proper error
@zotero.command()
@click.argument('parent', callback=parse_uuid_callback, required=True)
@click.pass_context
def template(ctx: click.Context, parent: ID):
    """
    Duplicates the standard Zotero Library template page to your workspace under the given parent page

    PARENT: Destination parent page ID or url
    """
    # Duplicate the block
    source = parse_uuid_callback(None, None, config.templates.zotero_template)
    target_id = str(uuid.uuid4())
    ctx.invoke(duplicate, source=source, parent=parent, target_id=target_id)

    # Extract the children from the command
    unotion = config.connections.notion_unofficial.client()
    page = unotion.get_block(target_id)
    children = list(page.children)

    collections_db = next(filter(lambda x: 'Collections' in x.title, children), None)
    if collections_db:
        click.echo(f'Found collection database ({parse_uuid(collections_db.id)})')

    refs_db = next(filter(lambda x: 'References' in x.title, children), None)
    if refs_db:
        click.echo(f'Found references database ({parse_uuid(refs_db.id)})')


@zotero.command()
@click.argument('references', callback=parse_uuid_callback, required=True)
@click.option('--force', is_flag=True, default=False,
              help='Ensures up to date items are also pushed to Zotero')
@click.option('-c', '--collections', callback=lambda c, p, x: parse_uuid_callback(c, p, x) if x else x, required=False,
              help='Collections database page ID or url to (optionally) add references to')
def refs(references: ID, collections: ID, force: bool):
    """
    Starts a one way Zotero references sync to Notion

    REFERENCES: References database page ID or url

    When collecitons option is specified Unofficial Notion Api access is required
    """
    notion = config.connections.notion.client()
    zotero = config.connections.zotero.client()

    RefsOneWaySync(notion, zotero, references, collections_id=collections, force=force).sync()


@zotero.command()
@click.argument('collections', callback=parse_uuid_callback, required=True)
@click.option('--force', is_flag=True, default=False,
              help='Ensures up to date items are also pushed to Zotero')
def collections(collections: ID, force: bool):
    """
    Starts a one way Zotero references sync to Notion

    COLLECTIONS: Collections database page ID or url
    """
    notion = config.connections.notion.client()
    zotero = config.connections.zotero.client()

    CollectionsOneWaySync(notion, zotero, collections, force=force).sync()
