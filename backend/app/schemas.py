"""
Pydantic schemas for the backend API.
"""
from pydantic import BaseModel, Field

class TTSRequest(BaseModel):
    """
    Schema for incoming Text-to-Speech requests.
    Validates that the text is within limits and speed is in an acceptable range.
    """
    text: str = Field(..., min_length=1, max_length=1000)
    voice: str = "default"
    speed: float = Field(1.0, ge=0.5, le=2.0)

class VideoRequest(BaseModel):
    video_paths: list[str]
    audio_path: str
    output_path: str