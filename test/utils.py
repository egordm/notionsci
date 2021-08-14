import io
import json
import os
from contextlib import redirect_stdout

ASSETS_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "assets"))
TESTS_PAGE = "https://www.notion.so/NotionSci-Tests-22ecab6188d147ef83fa455e2694395b"


def load_asset_json(filename: str) -> dict:
    file = os.path.join(ASSETS_DIR, filename)
    with open(file, "r") as f:
        return json.loads(f.read())


def capture_cmd(fn):
    f = io.StringIO()
    code = 0
    with redirect_stdout(f):
        try:
            fn()
        except SystemExit as e:
            code = e.code
    return code, f.getvalue()
