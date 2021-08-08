import click
from tqdm import tqdm

from notion_research.config import config
from notion_research.connections.notion import iter_items, SortObject, SortDirection


@click.group()
def sync():
    pass


@sync.command()
@click.option('-db', '--database')
def zotero(database: str):
    database = config.connections.notion.client().database(database)
    # notion_items = {
    #     item.get_property('ID').value(): item.get_property('Modified At').value()
    #     for item in tqdm(iter_items(database.query_all(
    #         sorts=[SortObject(property='Modified At', direction=SortDirection.descending)]
    #     )), desc='Loading existing Notion items')
    # }

    zotero_items = config.connections.zotero.client().all_items_tree()

    # zotero

    print(config)
    print(database)
