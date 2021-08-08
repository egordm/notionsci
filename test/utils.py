import json
import os

ASSETS_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "assets"))


def load_asset_json(filename: str) -> dict:
    file = os.path.join(ASSETS_DIR, filename)
    with open(file, "r") as f:
        return json.loads(f.read())
