from pathlib import Path


def get_root_path() -> Path:
    return Path(__file__).parent.parent


def get_path() -> Path:
    return get_root_path().parent
