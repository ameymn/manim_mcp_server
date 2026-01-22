from pathlib import Path

from pydantic import BaseModel, Field, model_validator

# Project root directory (parent of src/)
PROJECT_ROOT = Path(__file__).parent.parent.parent

class Settings(BaseModel):
    """Settings with pydantic validation"""

    output_dir: Path = Field(default=PROJECT_ROOT)  # Manim creates videos/ inside this
    code_dir: Path = Field(default=PROJECT_ROOT / "code")  # Python code files go here
    timeout: int = Field(default=300, ge=10, le=3600)


    @model_validator(mode="after")
    def create_directories(self):
        """Create directories"""
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.code_dir.mkdir(parents=True, exist_ok=True)
        return self


settings = Settings()

