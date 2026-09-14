from fastmcp import FastMCP
from core.ldraw_model import add_part, add_parts_batch, list_parts, remove_part
from core.parts_library import load_parts_index, search_parts
from core.renderer import render_view
from core.part_geometry import get_part_geometry, rotation_to_stand_upright, bone_rotation

mcp = FastMCP("MocForge MCP")


@mcp.tool()
def add_part_tool(model_path: str, part: str, color: int, position: tuple[float, float, float], rotation_matrix: tuple[float, float, float, float, float, float, float, float, float]):
    """
    Adds a part to the LDraw model.

    Args:
        model_path (str): Path to the .ldr file to append the part to.
        part (str): The ID of the part to add (e.g. "3001").
        color (int): The LDraw color code of the part.
        position (tuple): A tuple representing the (x, y, z) position of the part.
        rotation_matrix (tuple): A tuple of 9 numbers representing the 3x3
            rotation matrix, in row-major order (row1, row1, row1, row2, row2, row2,
            row3, row3, row3). Use (1, 0, 0, 0, 1, 0, 0, 0, 1) for no rotation
            (identity matrix). If you don't know which rotation makes a part stand
            upright or point in a given direction, call rotation_to_stand_upright_tool
            or bone_rotation_tool first instead of guessing.
    """
    add_part(model_path, part, color, position, rotation_matrix)


@mcp.tool()
def add_parts_batch_tool(model_path: str, parts: list[dict]):
    """
    Adds many parts to the LDraw model in a single call, instead of one call per part.
    Use this for any model with more than a handful of parts — it's the same effect as
    calling add_part_tool repeatedly, just far cheaper.

    Args:
        model_path (str): Path to the .ldr file to append the parts to.
        parts (list[dict]): Each entry has the same fields as add_part_tool's arguments:
            {"part": "3001", "color": 4, "position": [x, y, z],
             "rotation_matrix": [9 numbers, row-major]}.

    Returns:
        int: The number of parts written.
    """
    return add_parts_batch(model_path, parts)


@mcp.tool()
def get_part_geometry_tool(part_id: str) -> dict | None:
    """
    Returns the REAL measured bounding box and native long axis for a part, computed from
    its actual LDraw geometry file — not guessed. Call this BEFORE placing any part whose
    size or orientation you're not already certain of, instead of placing it, rendering, and
    discovering it was the wrong size or pointing the wrong way.

    Args:
        part_id (str): The part ID (e.g. "3705" for Technic Axle 4).

    Returns:
        A dict {"x": [min,max], "y": [min,max], "z": [min,max],
        "size_x", "size_y", "size_z", "long_axis": "x"|"y"|"z"} in LDU
        (1 stud = 20 LDU, 1 plate = 8 LDU, 1 brick = 24 LDU), or None if the part
        could not be found/parsed.
    """
    return get_part_geometry(part_id)


@mcp.tool()
def rotation_to_stand_upright_tool(part_id: str) -> tuple[float, ...] | None:
    """
    Returns the 3x3 rotation matrix (row-major, ready to pass straight to add_part_tool's
    rotation_matrix argument) that stands this part's own measured long axis up along world
    Y. Use this instead of guessing a rotation for any elongated part (axle, liftarm, limb,
    bar, blade...) you want oriented vertically — it reads the part's real geometry rather
    than assuming every part is authored along the same axis (they are not: e.g. Technic
    axles run along local X, most Technic liftarms run along local Z).

    Args:
        part_id (str): The part ID.

    Returns:
        A 9-number tuple, or None if the part's geometry could not be measured.
    """
    return rotation_to_stand_upright(part_id)


@mcp.tool()
def bone_rotation_tool(dr: float, dy: float, part_id: str) -> tuple[float, ...] | None:
    """
    Returns the rotation matrix that points this part's own measured long axis along the 2D
    direction (dr, dy) in the world X/Y plane, instead of only ever straight up or straight
    sideways. Use this to tilt a structural part (axle, liftarm, limb) at an arbitrary angle
    between two joints/points — e.g. a bent leg segment running from a hip point to a knee
    point that isn't directly above it.

    Args:
        dr (float): Horizontal (world X) component of the target direction, in LDU.
        dy (float): Vertical (world Y) component of the target direction, in LDU.
        part_id (str): The part ID whose own measured long axis should point that way.

    Returns:
        A 9-number tuple, or None if the part's geometry could not be measured.
    """
    return bone_rotation(dr, dy, part_id)


@mcp.tool()
def list_parts_tool(model_path: str) -> list[str]:
    """
    Lists all parts currently present in the LDraw model.

    Args:
        model_path (str): Path to the .ldr file to read.

    Returns:
        list[str]: The raw LDraw lines (type 1) for each part found,
            in the order they appear in the file.
    """
    return list_parts(model_path)


@mcp.tool()
def remove_part_tool(model_path: str, part_index: int):
    """
    Removes a part from the LDraw model by its index.

    Args:
        model_path (str): Path to the .ldr file to modify.
        part_index (int): The index of the part to remove (0-based).
    """
    remove_part(model_path, part_index)


@mcp.tool()
def render_view_tool(
    model_path: str,
    output_path: str,
    width: int = 640,
    height: int = 480,
    viewpoint: str | None = None,
    camera_latitude: float | None = None,
    camera_longitude: float | None = None,
):
    """
    Renders a view of the LDraw model using LeoCAD, with control over the camera angle —
    no need to rewrite/rotate the model file yourself to see it from another side.

    Args:
        model_path (str): Path to the .ldr file to render.
        output_path (str): Path where the rendered image will be saved.
        width (int): Width of the output image in pixels.
        height (int): Height of the output image in pixels.
        viewpoint (str, optional): One of "front", "back", "left", "right", "top",
            "bottom", "home" — a preset camera angle. Mutually exclusive with
            camera_latitude/camera_longitude.
        camera_latitude (float, optional): Camera latitude in degrees around the
            model (0 = level with the model, 90 = straight down). Use together
            with camera_longitude for an arbitrary turntable angle, e.g. to check
            a model from several sides in a row (call this 3-4 times with
            different camera_longitude values, same model, no other changes).
        camera_longitude (float, optional): Camera longitude in degrees around
            the model (0/90/180/270 give roughly front/right/back/left).
    """
    return render_view(model_path, output_path, width, height,
                        viewpoint, camera_latitude, camera_longitude)


@mcp.tool()
def search_parts_tool(query: str) -> dict[str, str]:
    """
    Searches the LDraw parts library for parts whose name contains the query
    string (case-insensitive). Use this to find the correct part ID before
    calling add_part_tool.

    Args:
        query: Text to search for in part names (e.g. "brick 2 x 4", "wheel").

    Returns:
        A dict mapping part IDs to their names, for all matching parts.
    """
    index = load_parts_index()
    return search_parts(query, index)


if __name__ == "__main__":
    mcp.run()

