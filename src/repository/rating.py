from sqlalchemy.orm import Session
from models import Rating

def create_rating(db: Session, post_id: int, rate: int, user_id: int):
    rating = Rating(post_id=post_id, rate=rate, user_id=user_id)
    db.add(rating)
    db.commit()
    db.refresh(rating)
    return rating