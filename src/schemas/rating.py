from pydantic import BaseModel


class RatingResponse(BaseModel):
    id: int
    post_id: int
    rating: int
    user_id: int

    class Config:
        orm_mode = True


class AverageRatingResponse(BaseModel):
    average_rating: float