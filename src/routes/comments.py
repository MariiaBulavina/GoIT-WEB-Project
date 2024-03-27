from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from src.database.models import UserRole
from src.repository import comments as comments_repository
from src.database.db import get_db
from src.schemas.comments import CommentModel, CommentResponse
from src.services.auth import auth_service
from src.repository import posts as posts_repository


router = APIRouter(tags=["comments"])

@router.post("/{post_id}/comments", response_model=CommentResponse)
async def create_comment_for_post(post_id: int, comment_data: CommentModel, db: Session = Depends(get_db),  user=Depends(auth_service.get_current_user)):

    post = await posts_repository.get_post(post_id, db)
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found") 
    
    comment = await comments_repository.create_comment(db, post_id, comment_data, user)

    if not comment:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Failed to create comment")
    return comment


@router.get("/comments/{comment_id}", response_model=CommentResponse)
async def read_comment(comment_id: int, db: Session = Depends(get_db), user=Depends(auth_service.get_current_user)):
    comment = await comments_repository.get_comment(db, comment_id)
    if not comment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Comment not found")
    return comment


@router.get("/{post_id}/comments", response_model=List[CommentResponse])

async def read_comment_for_post(post_id: int, db: Session = Depends(get_db), user=Depends(auth_service.get_current_user)):

    
    comments = await comments_repository.get_comments_for_post(post_id, db)

    if not comments:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Comments not found")
    
    return comments


@router.put("/comments/{comment_id}", response_model=CommentResponse)
async def update_existing_comment(comment_id: int, comment_data: CommentModel, db: Session = Depends(get_db), user=Depends(auth_service.get_current_user)):
    comment = await comments_repository.update_comment(db, comment_id, comment_data, user)
    if not comment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Comment not found")
    return comment


@router.delete("/comments/{comment_id}", response_model=CommentResponse)
async def delete_existing_comment(comment_id: int, db: Session = Depends(get_db), user=Depends(auth_service.get_current_user)):

    if user.user_role != UserRole.moderator and user.user_role != UserRole.admin:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You do not have permission to delete this comment")
    
    comment = await comments_repository.delete_comment(db, comment_id)
    if not comment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Comment not found")
    return comment
