import unittest

from notionsci.connections.notion.common import QueryResult
from utils import load_asset_json


class TestNotion(unittest.TestCase):
    def test_parse_items(self):
        data = load_asset_json('notion_database_items.json')

        result = QueryResult.from_dict(data)
        u = 0
