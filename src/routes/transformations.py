from cloudinary import CloudinaryImage
from fastapi import APIRouter, Request, Depends

from src.database.db import get_db
from src.services.posts import post_service
from src.services.auth import auth_service

router = APIRouter(prefix="/transformations", tags=["transformations"])


@router.post("/resize/{post_id}")
async def resize(
    request: Request,
    post_id: int,
    width: int,
    height: int,
    db=Depends(get_db),
    user=Depends(auth_service.get_current_user),
):
    return await post_service.resize_post(
        post_id=post_id, width=width, height=height, user=user, db=db
    )


@router.post("/filter/{post_id}")
async def add_filter(
    request: Request,
    post_id: int,
    filter: str,
    db=Depends(get_db),
    user=Depends(auth_service.get_current_user),
):
    return await post_service.add_filter(
        post_id=post_id, filter=filter, user=user, db=db
    )