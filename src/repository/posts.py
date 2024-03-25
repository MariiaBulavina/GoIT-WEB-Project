from datetime import datetime

import cloudinary.uploader
from sqlalchemy import text, and_
from sqlalchemy.orm import Session

from src.database.models import Post, User


async def add_post(post_url: str, public_id: str, description: str, user: User, db: Session):
    
    post = Post(
        post_url=post_url,
        public_id=public_id,
        description=description,
        user_id=user.id,
        created_at=datetime.now(),
        updated_at=datetime.now(),
    )
    post.tags = []
    db.add(post)
    db.commit()
    db.refresh(post)
    
    return post


async def delete_post(post_id: int, db: Session):
    post = (
        db.query(Post)
        .filter(Post.id == post_id)
        .first()
    )
    if post:
        cloudinary.uploader.destroy(post.public_id)
        db.delete(post)
        db.commit()
    return post


async def edit_description(post_id: int, description: str, db: Session):
    post = (
        db.query(Post)
        .filter(Post.id == post_id)
        .first()
    )
    if post:
        post.description = description
        post.tags = []
        post.updated_at = datetime.now()
        db.commit()
    return post


async def get_posts(user: User, db: Session):
    return db.query(Post).filter(Post.user_id == user.id).all()


async def get_post(post_id: int, db: Session):
    return (
        db.query(Post)
        .filter(Post.id == post_id)
        .first()
    )