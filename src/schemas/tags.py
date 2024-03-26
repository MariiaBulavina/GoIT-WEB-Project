from pydantic import BaseModel
from typing import List, Optional

class TagModel(BaseModel):
    tag_name: Optional[str]

class TagResponse(BaseModel):
    
    id: int
    tag: str
    created_at: str
    updated_at: str
    user_id: int

    class Config:
        orm_mode = True
