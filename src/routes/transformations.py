from typing import Literal

from fastapi import APIRouter, Request, Depends, status
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from src.database.db import get_db
from src.services.posts import post_service
from src.services.auth import auth_service
from src.services.qrcode_creation import generate_qrcode
from src.database.models import User


router = APIRouter(prefix="/transformations", tags=["transformations"])

@router.post("/resize/{post_id}", status_code=status.HTTP_201_CREATED)
async def resize(
    request: Request,
    post_id: int,
    width: int,
    height: int,
    db: Session = Depends(get_db),
    user: User = Depends(auth_service.get_current_user),
):
    """
    Function to resize post and generate a QR code for the transformed post URL.

    :param request: Request: HTTP request
    :param post_id: int: Post id
    :param width: int: Post width
    :param height: int: Post height
    :param db: Session: Connection to the database
    :param user: User: The currently authenticated user
    :return: StreamingResponse: QR code image for the transformed post URL
    """
    transformed_post = await post_service.resize_post(post_id=post_id, width=width, height=height, user=user, db=db)
    qr_code_buffer = generate_qrcode(transformed_post.transformed_post_url)

    return StreamingResponse(qr_code_buffer, media_type="image/png")


@router.post("/filter/{post_id}", status_code=status.HTTP_201_CREATED)
async def add_filter(
    request: Request,
    post_id: int,
    filter: Literal["al_dente", "athena", "audrey", "aurora", "daguerre", "eucalyptus", "fes", "frost",
            "hairspray", "hokusai", "incognito", "linen", "peacock", "primavera", "quartz",
            "red_rock", "refresh", "sizzle", "sonnet", "ukulele", "zorro"],
    db: Session = Depends(get_db),
    user: User = Depends(auth_service.get_current_user),
):
    """
    Function to apply a filter to a specific post and generate a QR code for the transformed post URL.

    :param request: Request: HTTP request 
    :param post_id: int: Post id
    :param filter: Literal: The name of the filter to apply
    :param db: Session: The database session
    :param user: User: The currently authenticated user
    :return: StreamingResponse:  QR code image for the transformed post URL
    """
    transformed_post = await post_service.add_filter(post_id=post_id, filter=filter, user=user, db=db)
    qr_code_buffer = generate_qrcode(transformed_post.transformed_post_url)

    return StreamingResponse(qr_code_buffer, media_type="image/png")
