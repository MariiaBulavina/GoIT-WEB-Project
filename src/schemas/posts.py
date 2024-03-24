from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field
from src.database.models import Tag


class PostModel(BaseModel):
    description: str = Field('description', min_length=10, max_length=255)
    tags_text: Optional[str] = Field(None, max_length=25)


class PostResponse(BaseModel):
    id: int
    Posts_url: str
    user_id: int
    created_at: datetime
    updated_at: Optional[datetime]
    description: str
    tags: list[Tag]

    class Config:
        from_attributes = True

