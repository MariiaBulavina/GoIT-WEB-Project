from fastapi import APIRouter, Depends, HTTPException, Path
from sqlalchemy.orm import Session
from database import get_db
from schemas.rating import RatingResponse
from services import auth_service
from repository.rating import create_rating
from models import Post, User

router = APIRouter()

@router.post('/{post_id}/{rate}', response_model=RatingResponse)
async def create_rate(
    post_id: int,
    rate: int = Path(..., ge=1, le=5),
    db: Session = Depends(get_db),
    current_user: User = Depends(auth_service.get_current_user)
    ):
    # Перевірка, чи користувач може оцінювати світлини
    if current_user is None:
        raise HTTPException(status_code=401, detail="Unauthorized")

    # Перевірка, чи користувач не оцінює свої світлини
    post = db.query(Post).filter(Post.id == post_id).first()
    if post.user_id == current_user.id:
        raise HTTPException(status_code=400, detail="User cannot rate their own photo")

    # Створення рейтингу
    rating = create_rating(db=db, post_id=post_id, rate=rate, user_id=current_user.id)
    return rating
