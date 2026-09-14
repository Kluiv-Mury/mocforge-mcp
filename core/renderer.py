import subprocess
from config import settings
from pathlib import Path

VIEWPOINTS = ("front", "back", "left", "right", "top", "bottom", "home")


def render_view(model_path, output_path, width=640, height=480,
                 viewpoint=None, camera_latitude=None, camera_longitude=None):
    """
    Renders a view of the LDraw model using LeoCAD.

    Args:
        model_path (str): Path to the .ldr file to render.
        output_path (str): Path where the rendered image will be saved.
        width (int): Width of the output image in pixels.
        height (int): Height of the output image in pixels.
        viewpoint (str, optional): One of "front", "back", "left", "right",
            "top", "bottom", "home". Mutually exclusive with the
            camera_latitude/camera_longitude pair.
        camera_latitude (float, optional): Camera latitude in degrees around
            the model (used with camera_longitude). Lets you get an arbitrary
            turntable angle without rewriting the model file.
        camera_longitude (float, optional): Camera longitude in degrees
            around the model (used with camera_latitude).
    """
    args = [
        settings.leocad_executable,
        model_path,
        "-i", output_path,
        "-w", str(width),
        "-h", str(height),
    ]

    if viewpoint is not None:
        if viewpoint not in VIEWPOINTS:
            raise ValueError(f"viewpoint must be one of {VIEWPOINTS}, got {viewpoint!r}")
        args += ["--viewpoint", viewpoint]
    elif camera_latitude is not None or camera_longitude is not None:
        if camera_latitude is None or camera_longitude is None:
            raise ValueError("camera_latitude and camera_longitude must be given together")
        args += ["--camera-angles", str(camera_latitude), str(camera_longitude)]

    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    resultado = subprocess.run(args, capture_output=True, text=True)
    if resultado.returncode != 0:
        raise RuntimeError(f"Erro ao renderizar(código {resultado.returncode}): {resultado.stderr}")
    return output_path

