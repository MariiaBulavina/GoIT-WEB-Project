from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from repository.main_functions import create_tag, get_tag, update_tag, delete_tag
from database import get_db
from ..schemas.tags import TagModel, TagResponse

router = APIRouter()

@router.post("/", response_model=TagResponse)
def create_new_tag(tag_data: TagModel, db: Session = Depends(get_db)):
    tag = create_tag(db, tag_data)
    if not tag:
        raise HTTPException(status_code=400, detail="Failed to create tag")
    return tag

@router.get("/{tag_id}", response_model=TagResponse)
def read_tag(tag_id: int, db: Session = Depends(get_db)):
    tag = get_tag(db, tag_id)
    if not tag:
        raise HTTPException(status_code=404, detail="Tag not found")
    return tag

@router.put("/{tag_id}", response_model=TagResponse)
def update_existing_tag(tag_id: int, tag_data: TagModel, db: Session = Depends(get_db)):
    tag = update_tag(db, tag_id, tag_data)
    if not tag:
        raise HTTPException(status_code=404, detail="Tag not found")
    return tag

@router.delete("/{tag_id}", response_model=TagResponse)
def delete_existing_tag(tag_id: int, db: Session = Depends(get_db)):
    tag = delete_tag(db, tag_id)
    if not tag:
        raise HTTPException(status_code=404, detail="Tag not found")
    return tag
