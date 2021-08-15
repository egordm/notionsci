import io
import json
import os
from contextlib import redirect_stdout

ASSETS_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "assets"))


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
