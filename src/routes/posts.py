from fastapi import APIRouter, Request, Depends, HTTPException, UploadFile, File, status, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from src.database.db import get_db
from src.repository import posts as posts_repository
from src.schemas.posts import PostResponse, PostsByFilter
from src.services.auth import auth_service
from src.services.posts import post_service
from src.database.models import UserRole, User
from src.services.qrcode_creation import generate_qrcode


router = APIRouter(prefix="/posts", tags=["posts"])

@router.post("/", response_model=PostResponse)
async def add_post(
    request: Request,
    file: UploadFile = File(...),
    description: str = "",
    db: Session = Depends(get_db),
    user: User = Depends(auth_service.get_current_user),
):
    """
    Function to add new post.

    :param request: Request: HTTP request
    :param file: UploadFile: Upload image file
    :param description: str: Description of post
    :param db: Session: Connection to the database
    :param user: User: The currently authenticated user
    :return: Post
    """
    post_info = await post_service.upload_post(file=file)

    return await posts_repository.add_post(
        post_url=post_info["url"],
        public_id=post_info["public_id"],
        description=description,
        user=user,
        db=db,
    )


@router.delete("/{post_id}", response_model=PostResponse)
async def delete_post(
    request: Request,
    post_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(auth_service.get_current_user),
):
    """
    Function to delete post.

    :param request: Request: HTTP request
    :param post_id: int: Post id
    :param db: Session: Connection to the database
    :param user: User: The currently authenticated user
    :return: Post
    """
    post = await posts_repository.delete_post(post_id=post_id, db=db)

    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")
    
    if post.user_id != user.id and user.user_role != UserRole.admin:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You do not have permission to delete this post")
    
    return post


@router.put("/{post_id}", response_model=PostResponse)
async def edit_description(
    request: Request,
    post_id: int,
    description: str,
    db: Session = Depends(get_db),
    user: User = Depends(auth_service.get_current_user),
):
    """
    Function to edit post description.

    :param request: Request: HTTP request
    :param post_id: int: Post id
    :param description: str: New post description
    :param db: Session: Connection to the database
    :param user: User: The currently authenticated user
    :return: Post
    """
    post = await posts_repository.edit_description(
        post_id=post_id, description=description, db=db
    )
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")
    
    if post.user_id != user.id and user.user_role != UserRole.admin:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You do not have permission to edit this post")
    
    return post


@router.get("/my_posts", response_model=list[PostResponse])
async def get_my_posts(
    request: Request,
    db: Session = Depends(get_db),
    user: User = Depends(auth_service.get_current_user),
):
    """
    Function to get posts belonging to the current user.

    :param request: Request: HTTP request
    :param db: Session: Connection to the database
    :param user: User: The currently authenticated user
    :return: list[PostResponse]: List of posts
    """
    return await posts_repository.get_my_posts(user=user, db=db)


@router.get("/{post_id}", response_model=PostResponse)
async def get_post(
    request: Request,
    post_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(auth_service.get_current_user),
):
    """
    Function to get post.

    :param request: Request: HTTP request
    :param: post_id: int: Post id
    :param db: Session: Connection to the database
    :param user: User: The currently authenticated user
    :return: PostResponse: Post
    """
    post = await posts_repository.get_post(post_id=post_id, db=db)
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")
    return post


@router.get("/{post_id}/qrcode")
async def get_post_qrcode(post_id: int, db: Session = Depends(get_db), user: User = Depends(auth_service.get_current_user)):
    """
    Function to get post qrcode.

    :param post_id: int: Post id
    :param db: Session: Connection to the database
    :param user: User: The currently authenticated user
    :return: StreamingResponse
    """
    url = await posts_repository.get_post_url(post_id, db)

    if url is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")
    
    qr_code_buffer = generate_qrcode(url)

    return StreamingResponse(qr_code_buffer, media_type="image/png")


@router.get("/", response_model=PostsByFilter) 
async def search_posts(
    current_user: User = Depends(auth_service.get_current_user),
    db: Session = Depends(get_db),
    keyword: str = Query(default=None),
    tag: str = Query(default=None),
    min_rating: int = Query(default=None),
    max_rating: int = Query(default=None)
    
):
    """
    Function to get a list of messages based on the provided filters.

    :param current_user: User: The currently authenticated user
    :param db: Session: The database session
    :param keyword: str, optional: A keyword to search for in the post's title or description
    :param tag: str, optional: A tag to filter posts by
    :param min_rating: int, optional: The minimum rating for the posts to be returned
    :param max_rating: int, optional: The maximum rating for the posts to be returned
    :return: PostsByFilter
    """
    try:
        all_posts = await posts_repository.get_all_posts(current_user, db, keyword, tag, min_rating, max_rating)
        return all_posts
    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail=str(e))    
