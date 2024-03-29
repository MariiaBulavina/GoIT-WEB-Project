from datetime import datetime
from typing import List, Any

from fastapi import HTTPException, status
import cloudinary.uploader
from sqlalchemy import Column
from sqlalchemy.orm import Session

from src.database.models import Post, User, Tag, TransformedPost


async def add_post(post_url: str, public_id: str, description: str, user: User, db: Session) -> Post:
    
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


async def delete_post(post_id: int, db: Session) -> Post | None:
    post = (
        db.query(Post)
        .filter(Post.id == post_id)
        .first()
    )
    if post:
        cloudinary.uploader.destroy(post.public_id)
        post.tags = []
        db.delete(post)
        db.commit()
    return post


async def edit_description(post_id: int, description: str, db: Session) -> Post | None:
    post = (
        db.query(Post)
        .filter(Post.id == post_id)
        .first()
    )
    if post:
        post.description = description
        post.tags = post.tags
        post.updated_at = datetime.now()
        db.commit()
    return post


async def get_posts(db: Session) -> List[Post]:
    result =  db.query(Post).all()
    return result


async def get_my_posts(user: User, db: Session) -> List[Post]:
    result =  db.query(Post).filter(Post.user_id == user.id).all()
    return result



async def get_post(post_id: int, db: Session) -> Post | None:
    return (
        db.query(Post)
        .filter(Post.id == post_id)
        .first()
    )


async def get_post_url(post_id: int, db: Session) -> Column[str] | None:

    result = db.query(Post).filter(Post.id == post_id).first()
    if result is None:
        return None
    
    return result.post_url


async def add_tag_to_post(post: Post, tag: Tag, db: Session) -> Post:

    if tag in post.tags:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f'The tag {tag.tag} has already been added to this post')
    
    if len(post.tags) == 5:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='You cannot add more than 5 tags to one post')

    post.tags.append(tag)
    post.updated_at = datetime.now()
    db.commit()
    db.refresh(post)
    return post 


async def get_post_by_url(post_url: str, db: Session) -> Post | None:

    result = db.query(Post).filter(Post.post_url == post_url).first()
    if result is None:
        return None
    
    return result


async def get_transformed_post_by_url(transformed_post_url: str, db: Session) -> TransformedPost | None:

    result = db.query(TransformedPost).filter(TransformedPost.transformed_post_url == transformed_post_url).first()
    if result is None:
        return None
    
    return result


async def add_transformed_post(transformed_post_url: str, post_id: int, db: Session) -> TransformedPost:
    
    transformed_post = TransformedPost(
        transformed_post_url=transformed_post_url,
        post_id=post_id,
        created_at=datetime.now(),
    )
    db.add(transformed_post)
    db.commit()
    db.refresh(transformed_post)
    
    return transformed_post


async def get_transformed_post_url(transformed_post_id: int, db: Session) -> Any | None:

    result = db.query(TransformedPost).filter(TransformedPost.id == transformed_post_id).first()
    if result is None:
        return None
    
    return result.transformed_post_url