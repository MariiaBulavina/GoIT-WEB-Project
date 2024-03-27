from datetime import datetime

from pydantic import BaseModel
from typing import List, Optional


class TagModel(BaseModel):
    tag_name: str


class TagResponse(BaseModel):
    
    id: int
    tag: str
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        orm_mode = True
