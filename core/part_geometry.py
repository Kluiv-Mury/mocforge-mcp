"""
Ground-truth part geometry read from the local LDraw library, instead of an LLM (or anyone
else calling this server) guessing a part's size/orientation and finding out it was wrong
only after rendering.

Recursively reads a part's .dat file (and any sub-part .dat files it references, since many
parts — e.g. Technic axles — are themselves composed of smaller primitive .dat files),
accumulates every vertex actually drawn, and reports the real bounding box in LDU. That
answers, before ever placing the part: how big is it, and along which local axis does its
longest dimension run (useful for deciding how to orient it when standing something upright
or aligning it along an arbitrary direction).

Results are cached to data/geometry_cache.json (same pattern as parts_library.json) so this
expensive recursive parse only happens once per part across the life of the server.
"""
import atexit
import json
import math
import os
from pathlib import Path

from config import settings, BASE_DIR

SEARCH_SUBDIRS = ["parts", "p", os.path.join("parts", "s"), os.path.join("p", "8"), os.path.join("p", "48")]

_cache = None
_cache_dirty = False
_cache_path = BASE_DIR / "data" / "geometry_cache.json"

_dat_paths = {}
_points_cache = {}


def _load_cache():
    global _cache
    if _cache is not None:
        return _cache
    if _cache_path.exists():
        with open(_cache_path, "r", encoding="utf-8") as f:
            _cache = json.load(f)
    else:
        _cache = {}
    return _cache


def _save_cache():
    global _cache_dirty
    if not _cache_dirty or _cache is None:
        return
    _cache_path.parent.mkdir(parents=True, exist_ok=True)
    with open(_cache_path, "w", encoding="utf-8") as f:
        json.dump(_cache, f, indent=2)
    _cache_dirty = False


atexit.register(_save_cache)


def _norm(part_id):
    """LDraw writes sub-part references Windows-style ("s\\32523s01.dat"), which resolves to
    nothing on a POSIX filesystem — half the library references a sub-part that way, and an
    unresolved reference is dropped silently, leaving the part measured without it. Callers
    also pass bare ids where the files carry the extension, and both spellings must land on
    the same cache entry or every shared primitive gets parsed twice."""
    p = part_id.replace("\\", "/")
    return p[:-4] if p.lower().endswith(".dat") else p


def _find_dat(part_id):
    key = _norm(part_id)
    if key in _dat_paths:
        return _dat_paths[key]
    root = Path(settings.ldraw_library_path)
    found = None
    for d in SEARCH_SUBDIRS:
        p = root / d / (key + ".dat")
        if p.exists():
            found = p
            break
    _dat_paths[key] = found
    return found


def _mat_mul(a, v):
    return (
        a[0]*v[0] + a[1]*v[1] + a[2]*v[2],
        a[3]*v[0] + a[4]*v[1] + a[5]*v[2],
        a[6]*v[0] + a[7]*v[1] + a[8]*v[2],
    )


def compose_rot(a, b):
    """Pure rotation composition: returns the matrix for 'apply a, then apply b'."""
    return tuple(
        sum(b[3*r+k]*a[3*k+c] for k in range(3))
        for r in range(3) for c in range(3)
    )


def _local_points(part_id, _visiting=frozenset()):
    """
    Vertices of a part in its OWN coordinate space, so the result depends only on the file
    and can be cached and reused wherever that file is referenced. Primitives like stud.dat
    recur dozens of times per part and across nearly every part in the library; parsing them
    once per process instead of once per reference is what keeps the recursion cheap.
    """
    key = _norm(part_id)
    if key in _points_cache:
        return _points_cache[key]
    if key in _visiting:
        return []
    path = _find_dat(key)
    if not path:
        _points_cache[key] = []
        return []

    pts = []
    sub_visiting = _visiting | {key}
    with open(path, "r", encoding="utf-8", errors="replace") as f:
        for line in f:
            toks = line.split()
            if not toks:
                continue
            t = toks[0]
            if t == "1":
                x, y, z = (float(v) for v in toks[2:5])
                sub_mat = tuple(float(v) for v in toks[5:14])
                sub_part = toks[14]
                for p in _local_points(sub_part, sub_visiting):
                    wx, wy, wz = _mat_mul(sub_mat, p)
                    pts.append((x+wx, y+wy, z+wz))
            elif t in ("2", "3", "4", "5"):
                nums = [float(v) for v in toks[2:]]
                for i in range(0, len(nums) - 2, 3):
                    pts.append((nums[i], nums[i+1], nums[i+2]))

    _points_cache[key] = pts
    return pts


def get_part_geometry(part_id):
    """
    Returns the measured bounding box and native long axis for a part, computed from its
    real LDraw geometry (not guessed), cached after the first call.

    Returns a dict:
        {
          "x": [min, max], "y": [min, max], "z": [min, max],
          "size_x": .., "size_y": .., "size_z": ..,
          "long_axis": "x" | "y" | "z",
        }
    or None if the part could not be found/parsed.
    """
    global _cache_dirty
    cache = _load_cache()
    if part_id in cache:
        return cache[part_id]

    pts = _local_points(part_id)
    if not pts:
        cache[part_id] = None
        _cache_dirty = True
        return None

    xs = [p[0] for p in pts]; ys = [p[1] for p in pts]; zs = [p[2] for p in pts]
    size_x, size_y, size_z = max(xs)-min(xs), max(ys)-min(ys), max(zs)-min(zs)
    sizes = [("x", size_x), ("y", size_y), ("z", size_z)]
    long_axis = max(sizes, key=lambda s: s[1])[0]

    result = {
        "x": [round(min(xs), 2), round(max(xs), 2)],
        "y": [round(min(ys), 2), round(max(ys), 2)],
        "z": [round(min(zs), 2), round(max(zs), 2)],
        "size_x": round(size_x, 2), "size_y": round(size_y, 2), "size_z": round(size_z, 2),
        "long_axis": long_axis,
    }
    cache[part_id] = result
    _cache_dirty = True
    return result


# Rotations that map a part's own measured long axis onto world Y (i.e. stand it upright),
# derived and confirmed against real renders: local X needs a 90-degree turn about Z, local
# Z needs a 90-degree turn about Y followed by that same Z turn, local Y is already upright.
_ROT_IDENTITY = (1,0,0, 0,1,0, 0,0,1)
_ROT_Y90 = (0,0,1, 0,1,0, -1,0,0)
_ROT_Z90 = (0,-1,0, 1,0,0, 0,0,1)
_ROT_X90 = (1,0,0, 0,0,-1, 0,1,0)
_AXIS_TO_VERTICAL = {
    "x": _ROT_Z90,
    "z": compose_rot(_ROT_Y90, _ROT_Z90),
    "y": _ROT_IDENTITY,
}


def rotation_to_stand_upright(part_id):
    """
    Returns the 3x3 rotation matrix (as a flat 9-tuple, row-major, ready for add_part_tool)
    that stands this part's own measured long axis up along world Y — so callers never have
    to guess which axis a part was authored along or hand-derive the rotation themselves.
    Returns None if the part's geometry could not be measured.
    """
    geo = get_part_geometry(part_id)
    if geo is None:
        return None
    return _AXIS_TO_VERTICAL[geo["long_axis"]]


def bone_rotation(dr, dy, part_id):
    """
    Returns the rotation matrix that points this part's own measured long axis along the 2D
    direction (dr, dy) in the world X/Y plane — i.e. tilts a structural part to run at an
    arbitrary angle between two joints/points, not just straight up or straight sideways.
    theta is measured from local +X toward +Y. Returns None if geometry is unavailable.
    """
    geo = get_part_geometry(part_id)
    if geo is None:
        return None
    theta = math.atan2(dy, dr)
    c, s = math.cos(theta), math.sin(theta)
    rz = (c, -s, 0, s, c, 0, 0, 0, 1)
    axis = geo["long_axis"]
    if axis == "x":
        return rz
    if axis == "z":
        return compose_rot(_ROT_Y90, rz)
    return _ROT_IDENTITY
