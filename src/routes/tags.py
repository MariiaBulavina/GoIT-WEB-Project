from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from src.repository import tags as tags_repository
from src.repository import posts as posts_repository
from src.database.db import get_db
from src.schemas.tags import TagModel, TagResponse
from src.services.auth import auth_service
from src.database.models import User, UserRole

router = APIRouter(prefix='/tags', tags=["tags"])

@router.post("/", response_model=TagResponse)
async def create_new_tag(post_id: int, tag: TagModel, db: Session = Depends(get_db), user: User = Depends(auth_service.get_current_user)):
    """
    Function to create new tag.

    :param post_id: int: Post id
    :param tag_data: TagModel: Information of tag
    :param db: Session: Connection to the database
    :param user: User: The currently authenticated user
    :return: Tag object
    """
    tag = await tags_repository.create_tag(db, tag)
    post = await posts_repository.get_post(post_id=post_id, db=db)
    await posts_repository.add_tag_to_post(post, tag, db)

    return tag


@router.get("/{tag_name}", response_model=TagResponse)
async def read_tag(tag_name: str, db: Session = Depends(get_db), user: User = Depends(auth_service.get_current_user)):
    """
    Function to read tag.

    :param tag_name: str: Name of tag
    :param db: Session: Connection to the database
    :param user: User: The currently authenticated user
    :return: Tag object
    """
    tag = await tags_repository.get_tag_by_name(db, tag_name)
    if not tag:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tag not found")
    return tag


@router.put("/{tag_id}", response_model=TagResponse)
async def update_existing_tag(tag_id: int, tag_data: TagModel, db: Session = Depends(get_db), user: User = Depends(auth_service.get_current_user)):
    """
    Function to update existing tag.

    :param tag_id: int: Tag id
    :param tag_data: TagModel: Information of tag
    :param db: Session: Connection to the database
    :param user: User: The currently authenticated user
    :return: Tag object
    """
    if user.user_role != UserRole.admin and user.user_role != UserRole.moderator:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You do not have permission to change tags")

    tag = await tags_repository.update_tag(db, tag_id, tag_data)
    return tag


@router.delete("/{tag_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_existing_tag(tag_id: int, db: Session = Depends(get_db), user: User = Depends(auth_service.get_current_user)):
    """
    Function to delete existing tag.

    :param tag_id: int: Tag id
    :param db: Session: Connection to the database
    :param user: User: The currently authenticated user
    :return: Tag object
    """
    if user.user_role != UserRole.admin and user.user_role != UserRole.moderator:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You do not have permission to delete tags")

    await tags_repository.delete_tag(db, tag_id)
