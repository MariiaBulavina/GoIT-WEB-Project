from decimal import Decimal
from typing import List

from sqlalchemy.orm import Session
from sqlalchemy import and_, func, select
from fastapi import HTTPException, status

from src.database.models import PostRating, User, Post


async def create_rating(db: Session, post_id: int, rating: int, user: User) -> PostRating:
    """
    Function to create new rating.

    :param db: Session: Connection session to database
    :param post_id: int: id of the post being rated
    :param rating: int: New rating value (1 to 5 stars)
    :param user: User: Current user
    :return: PostRating: Created Post rating
    """
    post = db.query(Post).filter(Post.id == post_id).first()

    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Post not found')

    if post.user_id == user.id:
        raise HTTPException(status_code=400, detail="User cannot rating their own photo")

    already_voted = (db.query(PostRating).filter(and_(PostRating.post_id == post_id, PostRating.user_id == user.id)).first())

    if already_voted:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='You have already voted')

    created_rating = PostRating(post_id=post_id, rating=rating, user_id=user.id)
    db.add(created_rating)
    db.commit()
    db.refresh(created_rating)

    average_rating = await calculate_average_rating(post_id, db) 
    if average_rating:
        post.average_rating = average_rating
        db.commit()

    return created_rating
    

async def calculate_average_rating(post_id: int, db: Session) -> Decimal:
    """
    Function to calculate average rating for the post.

    :param post_id: int: id of the post which the rating is calculated
    :param db: Session: Connection session to database
    :return: Decimal: Average rating for the post as a decimal number
    """
    query = select(func.avg(PostRating.rating).label('average_rating')).where(PostRating.post_id == post_id)
    result = db.execute(query)
    rating = result.scalar()
    return rating


async def delete_rating(post_id: int, user_id: int, db: Session) -> PostRating:
    """
    Function to delete the rating given by a specific user to a specific post.

    :param post_id: int: id of the post which the rating is calculated
    :param user_id: int: id of the user who gave the rating
    :param db: Session: Connection session to database
    :return: PostRating: Deleted Post rating
    """

    rating = db.query(PostRating).filter(and_(PostRating.user_id == user_id, PostRating.post_id == post_id)).first()

    if not rating:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Rating not found')
    
    db.delete(rating)
    db.commit()

    post = db.query(Post).filter(Post.id == post_id).first()

    average_rating = await calculate_average_rating(post_id, db)
    
    if average_rating:
        post.average_rating = average_rating
        db.commit()

    return rating


async def get_user_ratings(user_id: int, db: Session) -> List[PostRating]:
    """
    Function to get ratings given by a specific user.

    :param user_id: int: id of the user who gave ratings
    :param db: Session: Connection session to database
    :return: List[PostRating]: List of ratings left by the user
    """
    result = db.query(PostRating).filter(PostRating.user_id == user_id).all()

    if not result:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Ratings not found')
    
    return result