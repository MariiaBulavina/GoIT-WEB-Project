from typing import Type

from fastapi import HTTPException, status
from sqlalchemy import and_, func
from sqlalchemy.orm import Session

from src.database.models import RatePost, User, Post, UserRole
from src.conf import messages


async def create_rate(post_id: int, rate: int, db: Session, user: User) -> RatePost:
    """
    Create a new rating for an post.

    :param post_id: ID of the post to be rated.
    :type post_id: int
    :param rate: RatePost value (1 to 5 stars).
    :type rate: int
    :param db: Database session.
    :type db: Session
    :param user: Current user.
    :type user: User
    :return: Created RatePost object.
    :rtype: RatePost
    """
    is_self_post = (
        db.query(Post)
        .filter(and_(Post.id == post_id, Post.user_id == user.id))
        .first()
    )
    already_voted = (
        db.query(RatePost)
        .filter(and_(RatePost.post_id == post_id, RatePost.user_id == user.id))
        .first()
    )
    post_exists = db.query(Post).filter(Post.id == post_id).first()
    if is_self_post:
        raise HTTPException(
            status_code=status.HTTP_423_LOCKED, detail=messages.OWN_POST
        )
    elif already_voted:
        raise HTTPException(
            status_code=status.HTTP_423_LOCKED, detail=messages.VOTE_TWICE
        )
    elif post_exists:
        new_rate = RatePost(post_id=post_id, rate=rate, user_id=user.id)
        db.add(new_rate)
        db.commit()
        db.refresh(new_rate)
        return new_rate


async def edit_rate(rate_id: int, new_rate: int, db: Session, user: User) -> Type[RatePost] | None:
    """
    Edit the rating for a given post.

    :param rate_id: ID of the rating to be edited.
    :type rate_id: int
    :param new_rate: New rating value (1 to 5 stars).
    :type new_rate: int
    :param db: Database session.
    :type db: Session
    :param user: Current user.
    :type user: User
    :return: Updated RatePost object.
    :rtype: Type[RatePost] | None
    """
    rate = db.query(RatePost).filter(RatePost.id == rate_id).first()
    if user.role in [UserRole.admin, UserRole.moderator] or rate.user_id == user.id:
        if rate:
            rate.rate = new_rate
            db.commit()
    return rate


async def delete_rate(rate_id: int, db: Session, user: User) -> Type[RatePost]:
    """
    Delete a rating.

    This function deletes a rating with the given ID. Only the user who created the rating or
    an admin/moderator can delete a rating. It removes the rating from the database and commits the changes.

    :param rate_id: ID of the rating to be deleted.
    :type rate_id: int
    :param db: Database session.
    :type db: Session
    :param user: Current user.
    :type user: User
    :return: Deleted RatePost object.
    :rtype: Type[RatePost]
    """
    rate = db.query(RatePost).filter(RatePost.id == rate_id).first()
    if rate:
        db.delete(rate)
        db.commit()
    return rate


async def calculate_rating(post_id: int, db: Session, user: User):
    """
    Calculate the average rating for an post.

    :param post_id: ID of the post for which the rating is calculated.
    :type post_id: int
    :param db: Database session.
    :type db: Session
    :param user: Current user.
    :type user: User
    :return: Dictionary containing the average rating and post URL.
    :rtype: dict
    """
    all_ratings = (db.query(func.avg(RatePost.rate)).filter(RatePost.post_id == post_id).scalar())
    post_url = db.query(Post.url).filter(Post.id == post_id).scalar()
    return {"average_rating": all_ratings, "post_url": str(post_url)}


async def show_my_ratings(db: Session, current_user) -> list[Type[RatePost]]:
    """
    Retrieve all ratings given by the current user.

    :param db: Database session.
    :type db: Session
    :param current_user: Current user.
    :type current_user: User
    :return: List of ratings given by the current user.
    :rtype: List[Type[RatePost]]
    """
    all_ratings = db.query(RatePost).filter(RatePost.user_id == current_user.id).all()
    return all_ratings


async def user_rate_post(user_id: int, post_id: int, db: Session, user: User) -> Type[RatePost] | None:
    """
    Retrieve the rating given by a specific user to a specific post.

    :param user_id: User ID.
    :type user_id: int
    :param post_id: Post ID.
    :type post_id: int
    :param db: Database session.
    :type db: Session
    :param user: Current user.
    :type user: User
    :return: RatePost given by the specified user to the specified post.
    :rtype: Type[RatePost] | None
    """
    user_p_rate = (
        db.query(RatePost)
        .filter(and_(RatePost.post_id == post_id, RatePost.user_id == user_id))
        .first()
    )
    return user_p_rate


async def user_with_posts(db: Session, user: User):
    """
    Retrieve posts associated with a specific user.

    :param db: Database session.
    :type db: Session
    :param user: Current user.
    :type user: User
    :return: Posts associated with the specified user.
    :rtype: List[Type[Post]] | None
    """
    user_w_posts = db.query(Post).all()
    return user_w_posts
