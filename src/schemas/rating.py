from pydantic import BaseModel
from typing import Optional

class RatingResponse(BaseModel):
    id: int
    post_id: int
    rate: int
    user_id: int

    class Config:
        orm_mode = True
