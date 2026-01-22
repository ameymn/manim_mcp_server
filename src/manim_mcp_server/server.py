import uuid
import subprocess

from pathlib import Path
from mcp.server.fastmcp import FastMCP
from pydantic import BaseModel, Field

from .config import settings
from .models import Segment, Project

mcp = FastMCP("manim-server")

projects: dict[str, "Project"] = {}

def generate_scene_code(project: Project, segment_id: str | None = None) -> str:
    """Assemble complete Manim scene from project segments.

    Handles two types of segments:
    - 'preamble': Code placed outside the class (imports, helper classes, functions)
    - 'construct': Code placed inside the construct() method
    """
    if segment_id:
        segments = [s for s in project.segments if s.id == segment_id]
    else:
        segments = project.segments

    # Separate segments by type
    preamble_segments = [s.manim_code for s in segments if s.code_type == "preamble"]
    construct_segments = [s.manim_code for s in segments if s.code_type == "construct"]

    def indent_code(code: str, spaces: int = 8) -> str:
        indent = " " * spaces
        lines = code.split("\n")
        return "\n".join(indent + line if line.strip() else line for line in lines)

    preamble_code = "\n\n".join(preamble_segments)
    construct_code = "\n\n".join(indent_code(c) for c in construct_segments)

    # Build the final code
    parts = ["from manim import *"]

    if preamble_code:
        parts.append(preamble_code)

    parts.append(f'''class GeneratedScene(Scene):
    def construct(self):
{construct_code}''')

    return "\n\n".join(parts) + "\n"

def run_manim(scene_file: Path, output_name: str, quality: str = "medium_quality", preview_mode: bool = False) -> tuple[bool, str, str | None]:
    """Run Manim to render a scene.

    Returns:
        Tuple of (success, message, output_path or None)
    """
    # Map quality strings to manim CLI flags and folder names
    quality_map = {
        "low_quality": ("l", "480p15"),
        "medium_quality": ("m", "720p30"),
        "high_quality": ("h", "1080p60"),
        "fourk_quality": ("k", "2160p60"),
    }
    quality_flag, quality_folder = quality_map.get(quality, ("m", "720p30"))

    cmd = [
        "manim", "render",
        str(scene_file), "GeneratedScene",
        "-q", quality_flag,
        "-o", output_name,
        "--media_dir", str(settings.output_dir),
    ]

    if preview_mode:
        cmd.append("-s")

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=settings.timeout)

        if result.returncode != 0:
            return False, f"Manim error: {result.stderr}", None

        # Find the actual output file
        # Manim organizes output by class name, not file name
        scene_name = "GeneratedScene"
        if preview_mode:
            # Images go to: media_dir/images/scene_name/output_name.png
            output_path = settings.output_dir / "images" / scene_name / f"{output_name}.png"
        else:
            # Videos go to: media_dir/videos/scene_name/quality_folder/output_name.mp4
            output_path = settings.output_dir / "videos" / scene_name / quality_folder / f"{output_name}.mp4"

        if output_path.exists():
            return True, "Render successful", str(output_path)
        else:
            return False, f"Render completed but output not found at {output_path}", None

    except subprocess.TimeoutExpired:
        return False, f"Render timed out after {settings.timeout} seconds", None

    except Exception as e:
        return False, f"Unexpected error: {str(e)}", None





@mcp.tool()
def create_project(name: str, quality: str = "medium_quality", background_color: str | None = None) -> dict:
    """Initilizes a new video project


    Args:
        name: The name of the project
        quality: The quality of the video
        background_color: The background color of the video


    Returns:
        A dictionary containing the project ID and creation date
    """
    project = Project(name=name, quality=quality, background_color=background_color)
    projects[project.id] = project


    return {"project_id": project.id, "name": project.name, "quality": project.quality, "background_color": project.background_color, "message": f"Project {project.name} created successfully"}
    


@mcp.tool()
def add_segment(project_id: str, manim_code: str, description: str = "", code_type: str = "construct") -> dict:
    """Add a segment with manim code to the project.

    Args:
        project_id: The project ID from create_project
        manim_code: Raw Manim code
        description: Optional description of what this segment does
        code_type: 'construct' (default) = code inside construct() method,
                   'preamble' = code outside class (imports, helper classes, functions)

    Returns:
        Segment info with segment_id
    """
    if project_id not in projects:
        return {"error": f"Project with ID {project_id} not found"}

    if code_type not in ("construct", "preamble"):
        return {"error": f"Invalid code_type '{code_type}'. Must be 'construct' or 'preamble'"}

    project = projects[project_id]

    segment = Segment(manim_code=manim_code, description=description, code_type=code_type)

    project.segments.append(segment)

    return {
        "segment_id": segment.id,
        "project_id": project_id,
        "code_type": code_type,
        "total_segments": len(project.segments),
        "message": "Segment added successfully",
    }


@mcp.tool()
def preview(project_id: str, segment_id: str | None = None,) -> dict:
    """Generate a preview image of the project or a specific segment


    Args:
        project_id: The project ID
        segement_id: Optional - preview only this segment

    Returns:
        Path to the preview image
    """

    if project_id not in projects:
        return {"error": f"Project '{project_id}' not found"}

    project = projects[project_id]

    if not project.segments:
        return {"error": "Project has no segments. Use add_segment first"}

    scene_code = generate_scene_code(project,segment_id)

    scene_file = settings.code_dir / f"{project.id}_preview.py"
    scene_file.write_text(scene_code)

    success, message, preview_path = run_manim(
        scene_file=scene_file,
        output_name=f"{project.id}_preview",
        quality=project.quality,
        preview_mode=True,
    )

    if not success:
        return {"error": message}

    return {
        "preview_path": preview_path,
        "project_id": project_id,
        "message": "Preview generated successfully",
    }

@mcp.tool()
def edit_segment(project_id:str, segment_id:str,manim_code:str,description:str | None = None,)->dict:
    """Edit an existing segment's Manin code.

    Args:
        project_id: The project ID
        segment_id: The segmen ID to edit
        manim_code: New Manim code
        description: Optional new description


    Returns:
        Updated segment info
    """

    if project_id not in projects:
        return {"error": f"Project '{project_id}' not found"}

    project = projects[project_id]
    
    segment = next((s for s in project.segments if s.id == segment_id), None)

    if not segment:
        return {"error": f"Segment '{segment_id}' not found"}


    segment.manim_code=manim_code

    if description is not None:
        segment.description=description

    return {"segment_id": segment.id,"message": "Segment updated successfully"}


@mcp.tool()
def render(project_id: str)->dict:
    """Render the final video.

    Args:
        project_id: The project ID

    Returns:
        Path to rendered video"""

    if project_id not in projects:
        return{"error": f"Project '{project_id}' not found"}

    project = projects[project_id]

    if not project.segments:
        return{"error": "Project has no segments. Use add_segment first."}

    scene_code = generate_scene_code(project)
    scene_file = settings.code_dir / f"{project.id}_final.py"
    scene_file.write_text(scene_code)

    success, message, video_path = run_manim(
        scene_file=scene_file,
        output_name=project.id,
        quality=project.quality,
        preview_mode=False,
    )

    if not success:
        return {"error": message}

    return {"video_path": video_path, "message": f"Video rendered: {video_path}"}


if __name__=="__main__":
    mcp.run()