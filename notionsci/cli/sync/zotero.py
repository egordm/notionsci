import uuid

import click

from notionsci.cli.notion import duplicate
from notionsci.config import config
from notionsci.connections.notion import parse_uuid, parse_uuid_callback, BlockType, block_type_filter
from notionsci.connections.zotero import ID
from notionsci.sync.zotero import RefsSync, CollectionsSync
from notionsci.utils import take_1


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
    notion = config.connections.notion.client()
    page = notion.page_get(target_id, with_children=True)

    click.echo(f'Created page ({parse_uuid(page.id)})')

    collections_db = take_1(page.get_children(child_database_filter('Zotero Collections')))
    if collections_db:
        click.echo(f'Found collection database ({parse_uuid(collections_db.id)})')

    refs_db = take_1(page.get_children(child_database_filter('Zotero References')))
    if refs_db:
        click.echo(f'Found references database ({parse_uuid(refs_db.id)})')


def child_database_filter(title: str):
    type_filter = block_type_filter(BlockType.child_database)
    return lambda b: type_filter(b) and b.child_database.title == title


@zotero.command()
@click.argument('template', callback=parse_uuid_callback, required=True)
@click.option('--force', is_flag=True, default=False,
              help='Ensures up to date items are also pushed to Zotero')
def refs(template: ID, force: bool):
    """
    Starts a one way Zotero references sync to Notion

    TEMPLATE: Template page ID or url
    """
    notion = config.connections.notion.client()
    zotero = config.connections.zotero.client()
    sync_config = config.sync.zotero.get('refs', {})

    template_page = notion.page_get(template, with_children=True)
    references = take_1(template_page.get_children(child_database_filter('Zotero References')))
    collections = take_1(template_page.get_children(child_database_filter('Zotero Collections')))

    if not references or not collections:
        raise Exception('Please check whether child database called "Zotero References" and "Zotero Collections" '
                        'exist in given template')

    RefsSync(
        notion, zotero,
        references.id,
        collections_id=collections.id,
        force=force,
        **sync_config
    ).sync()


@zotero.command()
@click.argument('template', callback=parse_uuid_callback, required=True)
@click.option('--force', is_flag=True, default=False,
              help='Ensures up to date items are also pushed to Zotero')
def collections(template: ID, force: bool):
    """
    Starts a one way Zotero references sync to Notion

    TEMPLATE: Template page ID or url
    """
    notion = config.connections.notion.client()
    zotero = config.connections.zotero.client()

    template_page = notion.page_get(template, with_children=True)
    collections = next(iter(template_page.get_children(child_database_filter('Zotero Collections'))), None)

    CollectionsSync(notion, zotero, collections.id, force=force).sync()
