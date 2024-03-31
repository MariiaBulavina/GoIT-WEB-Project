from typing import Literal

from fastapi import APIRouter, Request, Depends
from fastapi.responses import StreamingResponse

from src.database.db import get_db
from src.services.posts import post_service
from src.services.auth import auth_service
from src.services.qrcode_creation import generate_qrcode


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
    transformed_post = await post_service.resize_post(post_id=post_id, width=width, height=height, user=user, db=db)
    qr_code_buffer = generate_qrcode(transformed_post.transformed_post_url)

    return StreamingResponse(qr_code_buffer, media_type="image/png")


@router.post("/filter/{post_id}")
async def add_filter(
    request: Request,
    post_id: int,
    filter: Literal["al_dente", "athena", "audrey", "aurora", "daguerre", "eucalyptus", "fes", "frost",
            "hairspray", "hokusai", "incognito", "linen", "peacock", "primavera", "quartz",
            "red_rock", "refresh", "sizzle", "sonnet", "ukulele", "zorro"],
    db=Depends(get_db),
    user=Depends(auth_service.get_current_user),
):
    transformed_post = await post_service.add_filter(post_id=post_id, filter=filter, user=user, db=db)
    qr_code_buffer = generate_qrcode(transformed_post.transformed_post_url)

    return StreamingResponse(qr_code_buffer, media_type="image/png")
