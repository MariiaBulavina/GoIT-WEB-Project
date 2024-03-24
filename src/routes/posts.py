from fastapi import APIRouter, Request, Depends, HTTPException, UploadFile, File

from src.database.db import get_db
from src.repository import posts as posts_repository
from src.schemas import PostResponse
from src.services.auth import auth_service
from src.services.posts import post_service

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
    post = await posts_repository.delete_post(post_id=post_id, user=user, db=db)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
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
        post_id=post_id, description=description, user=user, db=db
    )
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    return post


@router.get("/", response_model=list[PostResponse])
async def get_posts(
    request: Request,
    db=Depends(get_db),
    user=Depends(auth_service.get_current_user),
):
    return await posts_repository.get_posts(user=user, db=db)


@router.get("/{post_id}", response_model=PostResponse)
async def get_post(
    request: Request,
    post_id: int,
    db=Depends(get_db),
    user=Depends(auth_service.get_current_user),
):
    post = await posts_repository.get_post(post_id=post_id, user=user, db=db)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    return post
