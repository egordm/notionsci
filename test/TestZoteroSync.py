import io
import re
import unittest
from contextlib import redirect_stdout

from notionsci.cli import cli
from notionsci.config import config
from notionsci.connections.notion import parse_uuid_callback
from utils import TESTS_PAGE, capture_cmd


class TestZoteroSync(unittest.TestCase):
    def test_template(self):
        code, output = capture_cmd(
            lambda: cli(
                [
                    "sync",
                    "zotero",
                    "template",
                    parse_uuid_callback(None, None, TESTS_PAGE),
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
                    parse_uuid_callback(None, None, TESTS_PAGE),
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
                [
                    "sync",
                    "zotero",
                    "refs",
                    parse_uuid_callback(None, None, self.refs_db),
                    "--force",
                ]
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
                    parse_uuid_callback(None, None, self.refs_db),
                    "-c",
                    parse_uuid_callback(None, None, self.collection_db),
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
                    parse_uuid_callback(None, None, self.collection_db),
                    "--force",
                ]
            )
        )

        self.assertEqual(code, 0)
        self.assertIn("Reinforcement Learning", output)
        self.assertIn("Path Tracing", output)

    @classmethod
    def tearDownClass(cls) -> None:
        notion = config.connections.notion.client()
        unotion = config.connections.notion_unofficial.client()
        children = notion.client.blocks.children.list(
            "22ecab61-88d1-47ef-83fa-455e2694395b"
        )
        block_ids = list(map(lambda x: x["id"], children["results"]))
        unotion.delete_blocks(block_ids)


if __name__ == "__main__":
    unittest.main()
