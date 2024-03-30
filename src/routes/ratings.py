from fastapi import APIRouter, Depends, Path, HTTPException, status
from sqlalchemy.orm import Session

from src.database.db import get_db
from src.database.models import User, UserRole
from src.repository import ratings as repository_ratings
from src.schemas.ratings import RatingModel, RatingResponse
from src.schemas.posts import PostModel
from src.services.auth import auth_service
from src.services.roles import UserRole



router = APIRouter(prefix="/ratings", tags=["ratings"])

get_all_ratings = UserRole([UserRole.admin, UserRole.moderator, UserRole.user])
create_ratings = UserRole([UserRole.admin, UserRole.moderator, UserRole.user])
remove_ratings = UserRole([UserRole.admin, UserRole.moderator])
user_post_rate = UserRole([UserRole.admin])
rates_by_user = UserRole([UserRole.admin, UserRole.moderator, UserRole.user])
search_user_with_posts = UserRole([UserRole.admin, UserRole.moderator])


@router.post("/{image_id}/{rate}", response_model=RatingModel, dependencies=[Depends(create_ratings)])
async def create_rate(
    image_id: int,
    rate: int = Path(description="From one to five stars", ge=1, le=5),
    db: Session = Depends(get_db),
    current_user: User = Depends(auth_service.get_current_user),
):
    """
    Endpoint to create a rating for an image.

    :param image_id: The ID of the image to rate.
    :type image_id: int
    :param rate: The rating value, from one to five stars.
    :type rate: int
    :param db: Database session.
    :type db: Session
    :param current_user: The current authenticated user.
    :type current_user: User
    :return: Created rating.
    :rtype: RatingModel
    """
    new_rate = await repository_ratings.create_rate(image_id, rate, db, current_user)
    if new_rate is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No image with this ID.")
    return new_rate


@router.get("/all_my", response_model=list[RatingModel], dependencies=[Depends(rates_by_user)])
async def all_my_rates(
    db: Session = Depends(get_db),
    current_user: User = Depends(auth_service.get_current_user),
):
    """
    Endpoint to retrieves all ratings given by the current authenticated user.

    :param db: Database session.
    :type db: Session
    :param current_user: The current authenticated user.
    :type current_user: User
    :return: list of ratings given by the user.
    :rtype: list[RatingModel]
    """
    rates = await repository_ratings.show_my_ratings(db, current_user)
    if rates is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Rate not found")
    return rates


@router.get("/search_user_with_posts", response_model=list[ImageModel], dependencies=[Depends(search_user_with_posts)])
async def search_users_with_images(
    db: Session = Depends(get_db),
    current_user: User = Depends(auth_service.get_current_user),
):
    """
    Endpoint to retrieves a list of users who have uploaded images.

    :param db: Database session.
    :type db: Session
    :param current_user: The current authenticated user.
    :type current_user: User
    :return: list of users with images.
    :rtype: list[ImageModel]
    """
    users_with_images = await repository_ratings.user_with_images(db, current_user)
    if not users_with_images:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No user has added a post.")
    return users_with_images


@router.get("/{image_id}", response_model=RatingResponse, dependencies=[Depends(get_all_ratings)])
async def get_image_avg_rating(
    image_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(auth_service.get_current_user),
):
    """
    Endpoint to calculates and returns the average rating for a specific image.

    :param image_id: The ID of the image to calculate the average rating.
    :type image_id: int
    :param db: Database session.
    :type db: Session
    :param current_user: The current authenticated user.
    :type current_user: User
    :return: Average rating for the image.
    :rtype: RatingResponse
    """
    images_by_rating = await repository_ratings.calculate_rating(image_id, db, current_user)
    if images_by_rating is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Rate not found")
    return images_by_rating


@router.get("/user_image/{user_id}/{image_id}", response_model=RatingModel, dependencies=[Depends(user_post_rate)])
async def user_rate_image(
    user_id: int,
    image_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(auth_service.get_current_user),
):
    """
    Endpoint to retrieves the rating given by a specific user to a specific image.

    :param user_id: The ID of the user who gave the rating.
    :type user_id: int
    :param image_id: The ID of the image to retrieve the rating for.
    :type image_id: int
    :param db: Database session.
    :type db: Session
    :param current_user: The current authenticated user.
    :type current_user: User
    :return: Rating given by the user to the image.
    :rtype: RatingModel
    """
    rate = await repository_ratings.user_rate_image(user_id, image_id, db, current_user)
    if rate is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Rate not found")
    return rate


@router.delete(
    "/delete/{rate_id}",
    response_model=RatingModel,
    dependencies=[Depends(remove_ratings)],
)
async def delete_rate(
    rate_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(auth_service.get_current_user),
):
    """
    Endpoint to deletes a rating given by the current authenticated user.

    :param rate_id: The ID of the rating to be deleted.
    :type rate_id: int
    :param db: Database session.
    :type db: Session
    :param current_user: The current authenticated user.
    :type current_user: User
    :return: The deleted rating.
    :rtype: RatingModel
    """
    deleted_rate = await repository_ratings.delete_rate(rate_id, db, current_user)
    if deleted_rate is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Rate not found")
    return deleted_rate
