import uuid

from datetime import datetime

from pathlib import Path
from mcp.server.fastmcp import FastMCP
from pydantic import BaseModel, Field

from config import settings

mcp = FastMCP("manim-server")

projects: dict[str, "Project"] = {}

class ManimObject(BaseModel):
    """A single Manim object"""

    id: str = Field(..., description="The unique identifier of the object")
    type: str = Field(..., description="Object type: text, matrix, equation, circle, etc")
    properties: dict = Field(default_factory=dict, description="Object properties")
    position: list[float] | None  = Field(default=None, description="Object position in 3D space")
    color: str | None = Field(default=None, description="Object color")



class Animation(BaseModel):
    """ A single Manim animation"""

    type: str = Field(..., description="Animation type: write, fade_in, move, rotate, scale, etc")

    target: str | list[str] = Field(..., description="Object ID to animate")

    properties: dict = Field(default_factory=dict, description="Animation properties")



class Segment(BaseModel):
    """ A single segment containing objects and animations"""

    id: str = Field(default_factory=lambda: f"seg_{uuid.uuid4().hex[:8]}")
    objects: list[ManimObject] = Field(default_factory=list, description="Objects in the segment")

    animations: list[Animation] = Field(default_factory=list, description="Animations in the segment")

class Project(BaseModel):
    """ A video project containing multiple segments"""

    id: str = Field(default_factory=lambda: f"proj_{uuid.uuid4().hex[:8]}")
    name: str 
    quality:str = Field(default="medium_quality", description="Quality of the video: low_quality, medium_quality, high_quality")
    background_color: str | None = Field(default=None, description="Background color of the video")
    segments: list[Segment] = Field(default_factory=list, description="Segments in the project")
    created_at: datetime = Field(default_factory=datetime.now, description="Creation date and time")




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
def add_segment(project_id: str, objects: list[dict], animations: list[dict]) -> dict:
    """ Add a segment with objects and animations to a project

    Args:
        project_id: The ID of the project
        objects: List of object to create. Each object needs:
        - id: The unique identifier of the object
        - type: The type of the object
        - properties: The properties of the object
        - position: The position of the object in 3D space
        - color: The color of the object

        animations: List of animations to apply to the objects. Each animation needs:
        - type: The type of the animation
        - target: The ID of the object to animate
        - properties: The properties of the animation

    Returns:
        Segment info with segment_id
    """

    if project_id not in projects:
        return {"error": f"Project with ID {project_id} not found"}

    project = projects[project_id]

    manim_objects = [ManimObject(**obj) for obj in objects]

    manim_animations = [Animation(**anim) for anim in animations]


    segment = Segment(objects= manim_objects, animations=manim_animations,)

    project.segments.append(segment)

    return{
        "segment_id": segment.id,
        "project_id": project_id,
        "objects_count": len(manim_objects),
        "animations_count": len(manim_animations),
        "total_segments": len(project.segments),
        "message": f"Sgement added with {len(manim_objects)} objects and {len(manim_animations)} animations",
    }
