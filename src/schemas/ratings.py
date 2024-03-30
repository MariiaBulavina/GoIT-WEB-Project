from pydantic import BaseModel
from pydantic_settings import SettingsConfigDict


class RatingBase(BaseModel):
    rate: int


class RatingModel(RatingBase):
    model_config = SettingsConfigDict(from_attributes=True)
    id: int
    rate: int
    image_id: int
    user_id: int


class RatingResponse(BaseModel):
    average_rating: float | None


class AverageRatingResponse(BaseModel):
    average_rating: float
    image_url: str

