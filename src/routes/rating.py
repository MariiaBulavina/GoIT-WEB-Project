from typing import List

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from src.database.db import get_db
from src.schemas.rating import RatingResponse, AverageRatingResponse
from src.services.auth import auth_service
from src.repository import rating as repository_rating
from src.database.models import User, UserRole
from src.repository.posts import get_post


router = APIRouter(tags=['rating'])

@router.post('/{post_id}/rating', response_model=RatingResponse)
async def create_rating(
    post_id: int,
    rating: int = Query(description="From one to five stars", ge=1, le=5),
    db: Session = Depends(get_db),
    current_user: User = Depends(auth_service.get_current_user)
    ):
    
    if current_user is None:
        raise HTTPException(status_code=401, detail="Unauthorized")
   
    created_rating = await repository_rating.create_rating(db=db, post_id=post_id, rating=rating, user=current_user)
    return created_rating


@router.get('/{post_id}/rating', response_model=AverageRatingResponse)
async def get_post_rating(
    post_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(auth_service.get_current_user)
    ):
    
    post = await get_post(post_id, db)
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Post not found')
    return post


@router.delete('/{post_id}/rating', response_model=RatingResponse)
async def delete_rating(
    post_id: int,
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(auth_service.get_current_user)
    ):

    if current_user.user_role != UserRole.moderator and current_user.user_role != UserRole.admin:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You do not have permission to delete rating")
    
    deleted_rating = await repository_rating.delete_rating(post_id, user_id, db)
    return deleted_rating


@router.get('/users/{user_id}/rating', response_model=List[RatingResponse])
async def get_user_ratings(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(auth_service.get_current_user)
    ):

    if user_id != current_user.id and current_user.user_role != UserRole.admin and current_user.user_role != UserRole.moderator:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You do not have permission to view user ratings")

    result = await repository_rating.get_user_ratings(user_id, db)
    return result