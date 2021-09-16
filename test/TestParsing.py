import unittest

from notionsci.connections.notion.structures import QueryResult
from notionsci.connections.zotero import Item, Collection
from utils import load_asset_json


class TestParse(unittest.TestCase):
    def test_notion_parse_items(self):
        data = load_asset_json("notion_ref_pages.json")

        result = QueryResult.from_dict(data)

    def test_zotero_parse_items(self):
        data = load_asset_json("zotero_items.json")

        result = [Item.from_dict(i) for i in data]

    def test_zotero_parse_collections(self):
        data = load_asset_json("zotero_collections.json")

        result = [Collection.from_dict(i) for i in data]


if __name__ == "__main__":
    unittest.main()
