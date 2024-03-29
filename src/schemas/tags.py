from datetime import datetime

from pydantic import BaseModel
from typing import Optional


class TagModel(BaseModel):
    tag: str


class Tag(TagModel):
    id: int

    class Config:
        from_attributes = True


class TagResponse(BaseModel):
    
    id: int
    tag: str
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True
