import uuid
from collections import deque
from typing import Dict, Optional, List

import click
from tqdm import tqdm

from notionsci.cli.notion import duplicate
from notionsci.config import config
from notionsci.connections.notion import SortDirection, SortObject, Page, Parent, Property, \
    RelationItem, parse_uuid, parse_uuid_callback
from notionsci.connections.zotero import Item, ID, Collection, build_inherency_tree, generate_citekey
from notionsci.utils import key_by, flatten


@click.group()
def zotero():
    pass


# TODO: check if properties exist and throw proper error
@zotero.command()
@click.argument('parent', callback=parse_uuid_callback, required=True)
@click.pass_context
def template(ctx: click.Context, parent: ID):
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


def notion_fetch_all_pages(database: ID) -> Dict[ID, Page]:
    notion = config.connections.notion.client()
    return key_by(tqdm(notion.database_query_all(
        database,
        sorts=[SortObject(property='Modified At', direction=SortDirection.descending)]
    ), leave=False), lambda x: x.get_property('ID').value())


def zotero_fetch_collections(delete_children=False) -> Dict[ID, Collection]:
    zotero = config.connections.zotero.client()
    return key_by(zotero.all_collections_grouped(delete_children=delete_children), lambda i: i.key)


@zotero.command()
@click.option('--force', is_flag=True, default=False)
@click.option('-d', '--database', callback=parse_uuid_callback, required=True)
@click.option('-c', '--collections', callback=lambda c, p, x: parse_uuid(x) if x else x, required=False)
def refs(database: ID, collections: ID, force: bool):
    notion = config.connections.notion.client()
    zotero = config.connections.zotero.client()

    print('Loading existing Notion items')
    notion_pages: Dict[ID, Page] = notion_fetch_all_pages(database)

    notion_collection_pages = {}
    if collections:
        print('Loading existing Notion collection items')
        notion_collection_pages: Dict[ID, Page] = notion_fetch_all_pages(collections)

    print('Loading existing Zotero items')
    zotero_items: Dict[ID, Item] = key_by(zotero.all_items_grouped(), 'key')
    zotero_collections: Dict[ID, Collection] = key_by(zotero.all_collections_grouped(delete_children=False), 'key')
    collection_inherency = build_inherency_tree(zotero_collections.values())

    # Update or Create Pages
    items_to_upsert = [
        key for key in zotero_items.keys()
        if key not in notion_pages
           or zotero_items[key].data.date_modified > notion_pages[key].get_property('Modified At').value()
    ] if not force else list(zotero_items.keys())

    for key in tqdm(items_to_upsert, desc='Syncing citations', leave=False):
        page: Optional[Page] = notion_pages[key] if key in notion_pages else None
        item: Item = zotero_items[key]

        item_collections = set(flatten(
            [collection_inherency.get(col_key, []) for col_key in item.data.collections]
            + [item.data.collections or []]
        ))

        properties = {
            'ID': Property.as_rich_text(item.key),
            'Type': Property.as_select(item.data.item_type.value),
            'Cite Key': Property.as_title(generate_citekey(item)),
            'Title': Property.as_rich_text(item.title),
            'Authors': Property.as_rich_text(item.authors),
            'Publication Date': Property.as_rich_text(item.date),
            'Abstract': Property.as_rich_text(item.data.abstract),
            'URL': Property.as_url(item.data.url),
            'Publication': Property.as_rich_text(item.data.publication),
            'Tags': Property.as_multi_select([tag.tag for tag in item.data.tags]),
            'Collections': Property.as_multi_select([
                zotero_collections[col_key].title
                for col_key in item_collections
                if col_key in zotero_collections
            ]),
            'Parents': Property.as_relation([
                RelationItem(notion_collection_pages[k].id)
                for k in (item.data.collections or [])
                if k in notion_collection_pages
            ])
        }

        if page:
            page.extend_properties(properties)
            page = notion.page_update(page)
            tqdm.write(f'Updated: {page.get_property("Title").value()}')
        else:
            page = Page(
                parent=Parent.database(database),
                properties=properties
            )
            page = notion.page_create(page)
            tqdm.write(f'Created: {page.get_property("Title").value()}')

    # Delete non existing items
    items_to_delete = [
        key for key in notion_pages.keys()
        if key not in zotero_items
    ]
    for key in tqdm(items_to_delete, desc='Syncing citations', leave=False):
        page = notion_pages[key]
        page.archived = True
        page = notion.page_update(page)
        tqdm.write(f'Deleted: {page.get_property("Title").value()}')


def topo_sort(collections: List[Collection]) -> List[Collection]:
    result = []
    q = deque(collections)
    while len(q) > 0:
        item = q.popleft()
        result.append(item)
        if item.children:
            q.extend(item.children.values())
    return result


@zotero.command()
@click.option('--force', is_flag=True, default=False)
@click.option('-d', '--database', callback=parse_uuid_callback, required=True)
def collections(database: ID, force: bool):
    notion = config.connections.notion.client()
    zotero = config.connections.zotero.client()

    click.echo('Loading existing Notion items')
    notion_pages: Dict[ID, Page] = notion_fetch_all_pages(database)
    print('Loading existing Zotero items')
    zotero_collections: List[Collection] = topo_sort(zotero.all_collections_grouped(delete_children=True))

    zotero_notion_ids = {
        k: notion_pages[k].id
        for k in map(lambda x: x.key, zotero_collections) if k in notion_pages
    }

    click.echo('Upserting the collections')
    items_to_upsert = [
        x for x in zotero_collections
        if x.key not in notion_pages
    ] if not force else zotero_collections

    for collection in tqdm(items_to_upsert):
        key = collection.key
        page: Optional[Page] = notion_pages[key] if key in notion_pages else None

        properties = {
            'ID': Property.as_rich_text(collection.key),
            'Name': Property.as_title(collection.title),
            'Parent': Property.as_relation(
                [RelationItem(zotero_notion_ids[collection.data.parent_collection])]
                if collection.data.parent_collection else []
            ),
        }
        if page:
            page.extend_properties(properties)
            page = notion.page_update(page)
            click.echo(f'Updated: {page.get_property("Name").value()}')
        else:
            page = Page(
                parent=Parent.database(database),
                properties=properties
            )
            page = notion.page_create(page)
            click.echo(f'Created: {page.get_property("Name").value()}')
        zotero_notion_ids[key] = page.id
