import click

from notion_research.config import config


@click.group()
def sync():
    pass


@sync.command()
def zotero():
    print(config)
