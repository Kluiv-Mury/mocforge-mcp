from pathlib import Path
from config import settings, BASE_DIR
import json


def load_parts_index():

    path_cache = BASE_DIR / "data" / "parts_library.json"
    
    if path_cache.exists():
        with open(path_cache, "r") as arq:
            return json.load(arq)

    indice = {}
    parts_dir = Path(settings.ldraw_library_path) / "parts"

    for arq in parts_dir.glob("*.dat"):

        with open(arq, "r", encoding="utf-8") as f:
            piece = f.readline().strip().removeprefix("0 ")
        indice[arq.stem] = piece

    with open(path_cache, "w") as arq:
        json.dump(indice, arq, indent=2)

    return indice



def search_parts(query, index):
    """
    Searches the parts index for parts whose name contains the query string
    (case-insensitive).

    Args:
        query (str): Text to search for in part names.
        index (dict): The parts index, as returned by load_parts_index.

    Returns:
        dict: Subset of the index with only matching parts.
    """
    query = query.lower()
    return {part_id: name for part_id, name in index.items() if query in name.lower()}