from datetime import datetime
 
from pydantic import BaseModel
from typing import Optional


class CommentModel(BaseModel):
    comment_text: str

class CommentResponse(BaseModel):

    id: int
    comment_text: str
    created_at: datetime
    updated_at: Optional[datetime]
    post_id: Optional[int]
    user_id: int

    class Config:
        from_attributes = True

class CommentByUser(BaseModel):
    user_id: int
    comment: str  