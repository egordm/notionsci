import click

from notion_research.config import config


@click.group()
def sync():
    pass


@sync.command()
@click.option('-db', '--database')
def zotero(database: str):
    print(config)
    print(database)
