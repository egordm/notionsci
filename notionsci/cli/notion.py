import time

import click
import inquirer

from notionsci.config import config
from notionsci.connections.notion import parse_uuid_callback, ID, is_uuid, parse_uuid_or_str_callback


@click.group()
def notion():
    """
    Collection of general helper commands for notion api
    """
    pass


@notion.command()
@click.argument('source', callback=parse_uuid_callback)
@click.argument('parent', callback=parse_uuid_callback)
@click.option('--target_id', callback=parse_uuid_callback, required=False, default=None,
              help='Unique ID for the resulting page')
def duplicate(source: ID, parent: ID, target_id: ID):
    """
    Duplicates given SOURCE page into a PARENT page as a child page.

    SOURCE: Source page ID or url
    PARENT: Destination parent page ID or url

    Requires unofficial notion api
    """
    unotion = config.connections.notion_unofficial.client()

    source_block = unotion.get_block(source)
    if not source_block:
        raise Exception(f'Source page with uuid {source} does not exist ')

    parent_block = unotion.get_block(parent)
    if not parent_block:
        raise Exception(f'Parent page with uuid {parent} does not exist ')

    result_block = unotion.duplicate_page(source, parent_block, target_id)
    click.echo(f'Successfully duplicated {source_block.title} as {result_block.id}')


@notion.command()
@click.argument('workspace', required=False, callback=parse_uuid_or_str_callback)
def clear_trash(workspace):
    """
    Permanently deleted all _deleted_/_trashed_ pages in a workspace

    WORKSPACE: Workspace id or name to clean. If not specified a selection dialog is prompted.

    Requires unofficial notion api
    """
    unotion = config.connections.notion_unofficial.client()

    # Select a space
    space = None
    if is_uuid(workspace):
        space = unotion.get_space(workspace)
    else:
        spaces = list(unotion.get_spaces())
        if not workspace:
            workspace = inquirer.prompt([
                inquirer.List(
                    'space',
                    message="Select workspace to clean",
                    choices=[s.name for s in spaces],
                )
            ]).get('space', None)

        if workspace:
            space = next(filter(lambda s: s.name == workspace, spaces), None)

    if not space:
        raise Exception(f'Could not space matching "{workspace}"')

    click.echo(f'Cleaning Trash for Space: {space.name}')
    for i in range(1000):
        try:
            click.echo(f'- Cleaning page: {i}')
            trash = list(unotion.get_trash(space))
            if len(trash) == 0:
                break

            unotion.delete_blocks(trash)
            time.sleep(5)
        except:
            time.sleep(10)
            pass
