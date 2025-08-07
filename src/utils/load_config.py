import json

from utils.path import get_path

from typing import Any

def get_config() -> dict[str, Any]:
    try:
        with open(str(get_path() / "config.jsonc"), "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return {}


config = get_config()
