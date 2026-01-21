import uuid
from datetime import datetime

from pydantic import BaseModel, Field


class Segment(BaseModel):
    """A single segment containing Manim objects and animations."""

    id: str = Field(default_factory=lambda: f"seg_{uuid.uuid4().hex[:8]}")
    description: str = Field(default="")
    manim_code: str


class Project(BaseModel):
    """A video project containing multiple segments."""

    id: str = Field(default_factory=lambda: f"proj_{uuid.uuid4().hex[:8]}")
    name: str
    quality: str = Field(
        default="medium_quality",
        description="Quality of the video: low_quality, medium_quality, high_quality",)
        
    background_color: str | None = Field(default=None,description="Background color of the video",)

    segments: list[Segment] = Field(default_factory=list,description="Segments in the project",)

    created_at: datetime = Field(default_factory=datetime.now,description="Creation date and time",)
