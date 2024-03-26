from sqlalchemy.orm import Session
from datetime import datetime
from .models import Comment
from ..schemas.comments import CommentModel

def create_comment(db: Session, post_id: int, user_id: int, comment_data: CommentModel):
    comment = Comment(
        comment_text=comment_data.comment_text,
        created_at=datetime.now(),
        post_id=post_id,
        user_id=user_id
    )
    db.add(comment)
    db.commit()
    db.refresh(comment)
    return comment

def get_comment(db: Session, comment_id: int):
    return db.query(Comment).filter(Comment.id == comment_id).first()

def update_comment(db: Session, comment_id: int, comment_data: CommentModel):
    comment = db.query(Comment).filter(Comment.id == comment_id).first()
    if not comment:
        return None
    
    comment.comment_text = comment_data.comment_text
    comment.updated_at = datetime.now()
    db.commit()
    db.refresh(comment)
    return comment

def delete_comment(db: Session, comment_id: int):
    comment = db.query(Comment).filter(Comment.id == comment_id).first()
    if not comment:
        return None
    
    db.delete(comment)
    db.commit()
    return comment
