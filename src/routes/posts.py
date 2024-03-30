from fastapi import APIRouter, Request, Depends, HTTPException, UploadFile, File, status, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.exc import SQLAlchemyError

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
    db=Depends(get_db),
    user=Depends(auth_service.get_current_user),
):
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
    db=Depends(get_db),
    user=Depends(auth_service.get_current_user),
):
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
    db=Depends(get_db),
    user=Depends(auth_service.get_current_user),
):
    post = await posts_repository.edit_description(
        post_id=post_id, description=description, db=db
    )
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")
    
    if post.user_id != user.id and user.user_role != UserRole.admin:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You do not have permission to edit this post")
    
    return post


@router.get("/", response_model=list[PostResponse])
async def get_posts(
    request: Request,
    db=Depends(get_db),
    user=Depends(auth_service.get_current_user),
):
    return await posts_repository.get_posts(db=db)


@router.get("/my_posts", response_model=list[PostResponse])
async def get_my_posts(
    request: Request,
    db=Depends(get_db),
    user=Depends(auth_service.get_current_user),
):
    return await posts_repository.get_my_posts(user=user, db=db)


@router.get("/{post_id}", response_model=PostResponse)
async def get_post(
    request: Request,
    post_id: int,
    db=Depends(get_db),
    user=Depends(auth_service.get_current_user),
):
    post = await posts_repository.get_post(post_id=post_id, db=db)
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")
    return post


@router.get("/{post_id}/qrcode")
async def get_post_qrcode(post_id: int, db=Depends(get_db), user=Depends(auth_service.get_current_user)):
    
    url = await posts_repository.get_post_url(post_id, db)

    if url is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")
    
    qr_code_buffer = generate_qrcode(url)

    return StreamingResponse(qr_code_buffer, media_type="image/png")


@router.get("/transformed/{transformed_post_id}/qrcode")
async def get_transformed_post_qrcode(transformed_post_id: int, db=Depends(get_db), user=Depends(auth_service.get_current_user)):
    url = await posts_repository.get_transformed_post_url(transformed_post_id, db)

    if url is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")


@router.get("/search", response_model=PostsByFilter) #, dependencies=[Depends(all_roles)])
async def search_posts(
    current_user: User = Depends(auth_service.get_current_user),
    keyword: str = Query(default=None),
    tag: str = Query(default=None),
    min_rating: int = Query(default=None),
    db = Depends(get_db)
):
    """
    Endpoint to search for posts based on specified filters.

    :param db: Database session.
    :type db: Session
    :param current_user: Currently authenticated user.
    :type current_user: User
    :param keyword: Keyword to search for in image descriptions.
    :type keyword: str
    :param tag: Tag to filter posts by.
    :type tag: str
    :param min_rating: Minimum rating for posts.
    :type min_rating: int
    :return: Images matching the specified filters.
    :rtype: ImagesByFilter
    """
    try:
        all_posts = await posts_repository.get_all_posts(db, current_user, keyword, tag, min_rating)
        return all_posts
    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail=str(e))    
    qr_code_buffer = generate_qrcode(url)

    return StreamingResponse(qr_code_buffer, media_type="image/png")
