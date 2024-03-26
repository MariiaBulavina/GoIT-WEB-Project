from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from repository.comment_functions import create_comment, get_comment, update_comment, delete_comment
from database import get_db
from ..schemas.comments import CommentModel, CommentResponse

router = APIRouter()

@router.post("/{post_id}/comments", response_model=CommentResponse)
def create_comment_for_post(post_id: int, comment_data: CommentModel, db: Session = Depends(get_db)):
    comment = create_comment(db, post_id, comment_data)
    if not comment:
        raise HTTPException(status_code=400, detail="Failed to create comment")
    return comment

@router.get("/{comment_id}", response_model=CommentResponse)
def read_comment(comment_id: int, db: Session = Depends(get_db)):
    comment = get_comment(db, comment_id)
    if not comment:
        raise HTTPException(status_code=404, detail="Comment not found")
    return comment

@router.put("/{comment_id}", response_model=CommentResponse)
def update_existing_comment(comment_id: int, comment_data: CommentModel, db: Session = Depends(get_db)):
    comment = update_comment(db, comment_id, comment_data)
    if not comment:
        raise HTTPException(status_code=404, detail="Comment not found")
    return comment

@router.delete("/{comment_id}", response_model=CommentResponse)
def delete_existing_comment(comment_id: int, db: Session = Depends(get_db)):
    comment = delete_comment(db, comment_id)
    if not comment:
        raise HTTPException(status_code=404, detail="Comment not found")
    return comment
