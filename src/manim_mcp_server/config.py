from pathlib import Path

from pydantic import BaseModel, Field, model_validator

class Settings(BaseModel):
    """Settings with pydantic validation"""

    output_dir: Path = Field(default=Path("./output"))
    temp_dir: Path = Field(default=Path("./temp"))
    timeout: int = Field(default=300, ge=10, le=3600)


    @model_validator(mode="after")
    def create_directories(self):
        """Create directories"""
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.temp_dir.mkdir(parents=True, exist_ok=True)
        return self


settings = Settings()

