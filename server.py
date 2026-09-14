from fastmcp import FastMCP
from core.ldraw_model import add_part, list_parts, remove_part
from core.parts_library import load_parts_index, search_parts
from core.renderer import render_view

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
            (identity matrix).
    """
    add_part(model_path, part, color, position, rotation_matrix)


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
def render_view_tool(model_path: str, output_path: str, width: int = 640, height: int = 480):
    """
    Renders a view of the LDraw model using LeoCAD.

    Args:
        model_path (str): Path to the .ldr file to render.
        output_path (str): Path where the rendered image will be saved.
        width (int): Width of the output image in pixels.
        height (int): Height of the output image in pixels.
    """
    return render_view(model_path, output_path, width, height)


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

