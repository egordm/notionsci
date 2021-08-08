import unittest

from notionsci.connections.zotero.common import Item, Collection
from utils import load_asset_json


class TestZotero(unittest.TestCase):
    def test_parse_items(self):
        data = load_asset_json('zotero_items.json')

        result = [
            Item.from_dict(i)
            for i in data
        ]
        u = 0

    def test_parse_collections(self):
        data = load_asset_json('zotero_collections.json')

        result = [
            Collection.from_dict(i)
            for i in data
        ]
        u = 0
