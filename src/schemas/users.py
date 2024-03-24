from datetime import datetime
import enum

from pydantic import BaseModel, Field, EmailStr

from src.database.models import UserRole


class UserModel(BaseModel):
    username: str 
    email: EmailStr
    password: str = Field(min_length=6, max_length=8)


class UserDb(BaseModel):
    id: int
    username: str
    email: EmailStr
    created_at: datetime
    updated_at: datetime
    avatar: str
    user_role: UserRole

    class Config:
        from_attributes = True


class UserResponse(BaseModel):
    user: UserDb
    detail: str = 'User successfully created'


class TokenModel(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = 'bearer'


class RequestEmail(BaseModel):
    email: EmailStr


class UserProfile(BaseModel):

    id: int
    username: str
    email: EmailStr
    confirmed: bool
    avatar: str
    user_role: UserRole
    is_active: bool
    posts_number: int 
    comments_number: int 
    created_at: datetime
    updated_at: datetime


class Action(enum.Enum):
    change_user_role: str = 'change_user_role'
    ban: str = 'ban'
    unban: str = 'unban'