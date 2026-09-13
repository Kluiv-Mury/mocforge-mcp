from pathlib import Path
from config import settings
import json


def load_parts_index():

    path_cache = Path("data/parts_library.json")
    
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


result = load_parts_index()

print(result["1"], len(result))