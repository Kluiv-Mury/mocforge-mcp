from pathlib import Path
from config import settings, BASE_DIR
import json


_index = None


def load_parts_index():
    global _index
    if _index is not None:
        return _index

    path_cache = BASE_DIR / "data" / "parts_library.json"

    if path_cache.exists():
        with open(path_cache, "r") as arq:
            _index = json.load(arq)
        return _index

    indice = {}
    parts_dir = Path(settings.ldraw_library_path) / "parts"

    for arq in parts_dir.glob("*.dat"):

        with open(arq, "r", encoding="utf-8") as f:
            piece = f.readline().strip().removeprefix("0 ")
        indice[arq.stem] = piece

    path_cache.parent.mkdir(parents=True, exist_ok=True)
    with open(path_cache, "w") as arq:
        json.dump(indice, arq, indent=2)

    _index = indice
    return _index


def _normalize(text):
    """LDraw pads names to align the numbers ("Brick  2 x  4"), so a natural query like
    "brick 2 x 4" would never match on a raw substring test."""
    return " ".join(text.lower().split())


def search_parts(query, index):
    """
    Searches the parts index for parts whose name contains the query string
    (case-insensitive, ignoring differences in spacing).

    Args:
        query (str): Text to search for in part names.
        index (dict): The parts index, as returned by load_parts_index.

    Returns:
        dict: Subset of the index with only matching parts.
    """
    query = _normalize(query)
    return {part_id: name for part_id, name in index.items() if query in _normalize(name)}