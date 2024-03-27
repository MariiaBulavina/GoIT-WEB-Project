from datetime import datetime

from sqlalchemy.orm import Session
from sqlalchemy import  and_
from fastapi import HTTPException, status

from src.database.models import Comment, User, Post
from src.schemas.comments import CommentModel


async def create_comment(db: Session, post_id: int, comment_data: CommentModel, user: User):

    comment = Comment(
        comment_text=comment_data.comment_text,
        created_at=datetime.now(),
        post_id=post_id,
        user_id=user.id
    )
    db.add(comment)
    db.commit()
    db.refresh(comment)
    return comment


async def get_comment(db: Session, comment_id: int):
    return db.query(Comment).filter(Comment.id == comment_id).first()


async def update_comment(db: Session, comment_id: int, comment_data: CommentModel, user: User):

    comment = db.query(Comment).filter(and_(Comment.id == comment_id, Comment.user_id == user.id)).first()
    if not comment:
        return None
    
    if len(comment_data.comment_text) == 0:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Comment length cannot be 0')
    
    comment.comment_text = comment_data.comment_text
    comment.updated_at = datetime.now()
    db.commit()
    db.refresh(comment)
    return comment


async def delete_comment(db: Session, comment_id: int):

    comment = db.query(Comment).filter(Comment.id == comment_id).first()
    if not comment:
        return None
    
    db.delete(comment)
    db.commit()
    return comment


async def get_comments_for_post(post_id: int, db: Session):
    return  db.query(Comment).filter(Comment.post_id == post_id).all()

    

