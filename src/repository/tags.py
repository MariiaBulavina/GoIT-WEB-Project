from datetime import datetime

from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from src.database.models import Tag, Post
from src.schemas.tags import TagModel


async def create_tag(db: Session, tag_data: TagModel):

    tag = await get_tag_by_name(db, tag_data.tag_name)

    if tag:
        return tag
    
    tag = Tag(tag=tag_data.tag_name)
    db.add(tag)
    db.commit()
    db.refresh(tag)
    return tag


async def get_tag_by_name(db: Session, tag_name: str):
    return db.query(Tag).filter(Tag.tag == tag_name).first()


async def get_post_tags(post: Post, db: Session):

    result = []

    try:
        for tag in post.tags:
            result.append(tag)

    except AttributeError:
        ...

    return result


async def update_tag(db: Session, tag_id: int, tag_data: TagModel):

    tag = db.query(Tag).filter(Tag.id == tag_id).first()

    tag_find = db.query(Tag).filter(Tag.tag == tag_data.tag_name).first()

    if not tag:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tag not found")
    
    if tag_find:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f'Tag {tag_data.tag_name} already exists')
    
    tag.tag = tag_data.tag_name
    tag.updated_at = datetime.now()
    db.commit()
    db.refresh(tag)
    return tag


async def delete_tag(db: Session, tag_id: int):
    tag = db.query(Tag).filter(Tag.id == tag_id).first()
    if not tag:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tag not found")

    db.delete(tag)
    db.commit()
    return tag
