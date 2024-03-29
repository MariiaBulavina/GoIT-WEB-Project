from fastapi import APIRouter, Request, Depends, HTTPException, UploadFile, File, status
from fastapi.responses import StreamingResponse

from src.database.db import get_db
from src.repository import posts as posts_repository
from src.schemas.posts import PostResponse
from src.services.auth import auth_service
from src.services.posts import post_service
from src.database.models import UserRole
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
    
    qr_code_buffer = generate_qrcode(url)

    return StreamingResponse(qr_code_buffer, media_type="image/png")
