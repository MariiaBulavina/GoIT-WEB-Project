from sqlalchemy.orm import Session
from .models import Tag
from ..schemas.tags import TagModel

def create_tag(db: Session, tag_data: TagModel):
    tag = Tag(tag=tag_data.tag_name)
    db.add(tag)
    db.commit()
    db.refresh(tag)
    return tag

def get_tag(db: Session, tag_id: int):
    return db.query(Tag).filter(Tag.id == tag_id).first()

def update_tag(db: Session, tag_id: int, tag_data: TagModel):
    tag = db.query(Tag).filter(Tag.id == tag_id).first()
    if not tag:
        return None  # Або викинути помилку HTTPException
    
    tag.tag = tag_data.tag_name
    db.commit()
    db.refresh(tag)
    return tag

def delete_tag(db: Session, tag_id: int):
    tag = db.query(Tag).filter(Tag.id == tag_id).first()
    if not tag:
        return None  # Або викинути помилку HTTPException

    db.delete(tag)
    db.commit()
    return tag
