from pathlib import Path



def add_part(model_path, part, color, position, rotation_matrix):
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
    x, y, z = position
    r11, r12, r13, r21, r22, r23, r31, r32, r33 = rotation_matrix

    line = f"1 {color} {x} {y} {z} {r11} {r12} {r13} {r21} {r22} {r23} {r31} {r32} {r33} {part}.dat\n"

    Path(model_path).parent.mkdir(parents=True, exist_ok=True)
    with open(model_path, "a") as f:
        f.write(line)



def list_parts(model_path):
    """
    Lists all parts currently present in the LDraw model.

    Args:
        model_path (str): Path to the .ldr file to read.

    Returns:
        list[str]: The raw LDraw lines (type 1) for each part found,
            in the order they appear in the file.
    """
    with open(model_path, "r") as f:
        lines = f.readlines()

    parts = [line.strip() for line in lines if line.startswith("1 ")]

    return parts




def remove_part(model_path, part_index):
    """
    Removes a part from the LDraw model by its index.

    Args:
        model_path (str): Path to the .ldr file to modify.
        part_index (int): The index of the part to remove (0-based).
    """
    with open(model_path) as f:
        lines = f.readlines()
    parts = [line.strip() for line in lines if line.startswith("1 ")]
    parts.pop(part_index)

    with open(model_path, "w") as f:
        for part in parts:
            f.write(part + "\n")


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