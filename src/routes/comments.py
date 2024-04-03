from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from src.database.models import UserRole
from src.repository import comments as comments_repository
from src.database.db import get_db
from src.schemas.comments import CommentModel, CommentResponse
from src.services.auth import auth_service
from src.repository import posts as posts_repository


router = APIRouter(prefix="/comments", tags=["comments"])

@router.post("/", response_model=CommentResponse)
async def create_comment_for_post(post_id: int, comment_data: CommentModel, db: Session = Depends(get_db),  user=Depends(auth_service.get_current_user)):
    """
    Function to create comment for post.

    :param post_id: int: Post id
    :param comment_data: CommentModel: Text of comment
    :param db: Session: Connection to the database
    :param user: User: The currently authenticated user
    :return: Comment
    """
    post = await posts_repository.get_post(post_id, db)
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found") 
    
    comment = await comments_repository.create_comment(db, post_id, comment_data, user)

    if not comment:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Failed to create comment")
    return comment


@router.get("/{comment_id}", response_model=CommentResponse)
async def read_comment(comment_id: int, db: Session = Depends(get_db), user=Depends(auth_service.get_current_user)):
    """
    Function to read comment.

    :param comment_id: int: Comment id
    :param db: Session: Connection to the database
    :param user: User: The currently authenticated user
    :return: Comment
    """
    comment = await comments_repository.get_comment(db, comment_id)

    if not comment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Comment not found")
    return comment



@router.put("/{comment_id}", response_model=CommentResponse)
async def update_existing_comment(comment_id: int, comment_data: CommentModel, db: Session = Depends(get_db), user=Depends(auth_service.get_current_user)):
    """
    Function to update existing comment.

    :param comment_id: int: Comment id
    :param comment_data: CommentModel: New text of comment
    :param db: Session: Connection to the database
    :param user: User: The currently authenticated user
    :return: Comment
    """
    comment = await comments_repository.update_comment(db, comment_id, comment_data, user)
    
    if not comment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Comment not found")
    return comment


@router.delete("/{comment_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_existing_comment(comment_id: int, db: Session = Depends(get_db), user=Depends(auth_service.get_current_user)):
    """
    Function to delete existing comment.

    :param comment_id: int: Comment id
    :param db: Session: Connection to the database
    :param user: User: The currently authenticated user
    :return: Comment
    """
    if user.user_role != UserRole.moderator and user.user_role != UserRole.admin:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You do not have permission to delete this comment")
    
    comment = await comments_repository.delete_comment(db, comment_id)
    if not comment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Comment not found")
