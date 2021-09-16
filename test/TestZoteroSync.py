import re
import unittest

from notionsci.cli import cli
from notionsci.config import config
from notionsci.connections.notion import parse_uuid_or_url
from utils import capture_cmd


class TestZoteroSync(unittest.TestCase):
    def setUp(self) -> None:
        self.config = config

    def test_template(self):
        code, output = capture_cmd(
            lambda: cli(
                [
                    "sync",
                    "zotero",
                    "template",
                    parse_uuid_or_url(self.config.development.test_page),
                ]
            )
        )

        self.assertEqual(code, 0)
        self.assertIn("Found collection database", output)
        self.assertIn("Found references database", output)
        self.assertIn("Zotero Library", output)

    def setupTemplate(self):
        code, output = capture_cmd(
            lambda: cli(
                [
                    "sync",
                    "zotero",
                    "template",
                    parse_uuid_or_url(self.config.development.test_page),
                ]
            )
        )

        self.assertEqual(code, 0)
        self.collection_db = re.search(
            r"Found collection database \((.*)\)", output
        ).group(1)
        self.refs_db = re.search(r"Found references database \((.*)\)", output).group(1)

    def test_sync_refs(self):
        self.setupTemplate()

        code, output = capture_cmd(
            lambda: cli(
                ["sync", "zotero", "refs", parse_uuid_or_url(self.refs_db), "--force",]
            )
        )

        self.assertEqual(code, 0)
        self.assertIn("ShaderbasedAntialiasedDashed", output)
        self.assertIn("schrittwieserMasteringAtariGo2020", output)

    def test_sync_refs_with_collections(self):
        self.setupTemplate()

        code, output = capture_cmd(
            lambda: cli(
                [
                    "sync",
                    "zotero",
                    "refs",
                    parse_uuid_or_url(self.refs_db),
                    "-c",
                    parse_uuid_or_url(self.collection_db),
                    "--force",
                ]
            )
        )

        self.assertEqual(code, 0)
        self.assertIn("Loading existing Notion collections", output)
        self.assertIn("ShaderbasedAntialiasedDashed", output)
        self.assertIn("schrittwieserMasteringAtariGo2020", output)

    def test_sync_collections(self):
        self.setupTemplate()

        code, output = capture_cmd(
            lambda: cli(
                [
                    "sync",
                    "zotero",
                    "collections",
                    parse_uuid_or_url(self.collection_db),
                    "--force",
                ]
            )
        )

        self.assertEqual(code, 0)
        self.assertIn("Reinforcement Learning", output)
        self.assertIn("Path Tracing", output)

    @classmethod
    def tearDownClass(cls) -> None:
        try:
            notion = config.connections.notion.client()
            unotion = config.connections.notion_unofficial.client()
            children = notion.client.blocks.children.list(
                parse_uuid_or_url(config.development.test_page)
            )
            block_ids = list(map(lambda x: x["id"], children["results"]))
            unotion.delete_blocks(block_ids)
        except:
            pass


if __name__ == "__main__":
    unittest.main()
