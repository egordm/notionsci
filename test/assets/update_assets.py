import json
import os

from notionsci.config import config
from notionsci.connections.notion import parse_uuid_callback

assets_dir = os.path.abspath(os.path.dirname(__file__))

unotion = config.connections.notion_unofficial.client()
notion = config.connections.notion.client()

page = unotion.get_block(parse_uuid_callback(None, None, config.templates.zotero_template))
children = list(page.children)

collections_db_id = next(filter(lambda x: 'Collections' in x.title, children)).id
refs_db_id = next(filter(lambda x: 'References' in x.title, children)).id

notion_ref_pages = notion.client.databases.query(refs_db_id)
with open(os.path.join(assets_dir, 'notion_ref_pages.json'), 'w') as f:
    f.write(json.dumps(notion_ref_pages, indent=4))


zotero = config.connections.zotero.client()

zotero_collections = zotero.client.collections()
with open(os.path.join(assets_dir, 'zotero_collections.json'), 'w') as f:
    f.write(json.dumps(zotero_collections, indent=4))

zotero_items = zotero.client.items()
with open(os.path.join(assets_dir, 'zotero_items.json'), 'w') as f:
    f.write(json.dumps(zotero_items, indent=4))