from datetime import datetime

from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from src.database.models import Tag, Post
from src.schemas.tags import TagModel


async def create_tag(db: Session, tag_data: TagModel) -> Tag:
    """
    Function to create tag.

    :param db: Session: Connection session to database
    :param tag_data: TagModel: Tag
    :return: Tag
    """
    tag = await get_tag_by_name(db, tag_data.tag)

    if tag:
        return tag
    
    if len(tag_data.tag) == 0:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Tag length cannot be 0')
    
    tag = Tag(tag=tag_data.tag)
    db.add(tag)
    db.commit()
    db.refresh(tag)
    return tag


async def get_tag_by_name(db: Session, tag: str) -> Tag | None:
    """
    Function to get tag by name.

    :param db: Session: Connection session to database
    :param tag_name: str: Name of tag
    :return: Tag | None
    """
    return db.query(Tag).filter(Tag.tag == tag).first()


async def get_post_tags(post: Post, db: Session) -> list:
    """
    Function to get post tags.

    :param post: Post: Post tags of which we receive
    :param db: Connection session to database
    :return: List of tags
    """
    result = []

    try:
        for tag in post.tags:
            result.append(tag)

    except AttributeError:
        ...

    return result


async def update_tag(db: Session, tag_id: int, tag_data: TagModel) -> Tag:
    """
    Function to update tag.

    :param db: Session: Connection session to database
    :param tag_id: int: id of the tag
    :param tag_data: TagModel: description of the tag
    :return: Tag
    """
    tag = db.query(Tag).filter(Tag.id == tag_id).first()

    tag_find = db.query(Tag).filter(Tag.tag == tag_data.tag).first()

    if not tag:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tag not found")
    
    if tag_find:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f'Tag {tag_data.tag} already exists')
    
    if len(tag_data.tag) == 0:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Tag length cannot be 0')
    
    tag.tag = tag_data.tag
    tag.updated_at = datetime.now()
    db.commit()
    db.refresh(tag)
    return tag


async def delete_tag(db: Session, tag_id: int) -> Tag:
    """
    Function to delete tag.

    :param db: Session: Connection session to database
    :param tag_id: int: id of tag
    :return: Tag
    """
    tag = db.query(Tag).filter(Tag.id == tag_id).first()
    if not tag:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tag not found")

    db.delete(tag)
    db.commit()
    return tag
