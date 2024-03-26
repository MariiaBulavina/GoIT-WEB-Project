from pydantic import BaseModel
from typing import Optional

class CommentModel(BaseModel):
    comment_text: str

class CommentResponse(BaseModel):
    id: int
    comment_text: str
    created_at: str
    updated_at: str
    post_id: int
    user_id: int

    class Config:
        orm_mode = True
