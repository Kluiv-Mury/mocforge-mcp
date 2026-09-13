import subprocess
from config import settings
from pathlib import Path


def render_view(model_path, output_path, width=640, height=480):
    """
    Renders a view of the LDraw model using LeoCAD.

    Args:
        model_path (str): Path to the .ldr file to render.
        output_path (str): Path where the rendered image will be saved.
        width (int): Width of the output image in pixels.
        height (int): Height of the output image in pixels.
    """
    args = [
        settings.leocad_executable,
        model_path,
        "-i", output_path,
        "-w", str(width),
        "-h", str(height)
    ]
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    resultado = subprocess.run(args, capture_output=True, text=True)
    if resultado.returncode != 0:
        raise RuntimeError(f"Erro ao renderizar(código {resultado.returncode}): {resultado.stderr}")
    return output_path


render_view("data/models/test.ldr", "data/renders/test.png", 800, 600)