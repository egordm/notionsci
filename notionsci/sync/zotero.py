from typing import Dict, Optional

import click
from tqdm import tqdm

from notionsci.config import config
from notionsci.connections.notion import SortDirection, SortObject, Page, Parent, Property
from notionsci.connections.zotero import Item, ID, Collection, build_inherency_tree, generate_citekey
from notionsci.utils import key_by, flatten


@click.group()
def sync():
    pass


@sync.command()
@click.option('-db', '--database')
@click.option('--force', is_flag=True, default=False)
def zotero(database: str, force: bool = False):
    notion = config.connections.notion.client()
    database = notion.database(database)

    print('Loading existing Notion items')
    notion_items: Dict[ID, Page] = key_by(tqdm(database.query_all(
        sorts=[SortObject(property='Modified At', direction=SortDirection.descending)]
    ), leave=False), lambda x: x.get_property('ID').value())

    print('Loading existing Zotero items')
    zotero_items: Dict[ID, Item] = key_by(
        config.connections.zotero.client().all_items_grouped(), lambda i: i.key)
    zotero_collections: Dict[ID, Collection] = key_by(
        config.connections.zotero.client().all_collections_grouped(delete_children=False), lambda i: i.key)
    collection_inherency = build_inherency_tree(zotero_collections.values())

    # Update or Create Pages
    items_to_upsert = [
        key for key in zotero_items.keys()
        if key not in notion_items
           or zotero_items[key].data.date_modified > notion_items[key].get_property('Modified At').value()
    ] if not force else list(zotero_items.keys())

    for key in tqdm(items_to_upsert, desc='Syncing citations', leave=False):
        page: Optional[Page] = notion_items[key] if key in notion_items else None
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
            ])
        }

        if page:
            page.extend_properties(properties)
            page = notion.update_page(page)
            tqdm.write(f'Updated: {page.get_property("Title").value()}')
        else:
            page = Page(
                parent=Parent.database(database.id),
                properties=properties
            )
            page = notion.create_page(page)
            tqdm.write(f'Created: {page.get_property("Title").value()}')

    # Delete non existing items
    items_to_delete = [
        key for key in notion_items.keys()
        if key not in zotero_items
    ]
    for key in tqdm(items_to_delete, desc='Syncing citations', leave=False):
        page = notion_items[key]
        page.archived = True
        page = notion.update_page(page)
        tqdm.write(f'Deleted: {page.get_property("Title").value()}')

