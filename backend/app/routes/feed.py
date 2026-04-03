from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session
from sqlalchemy import desc
from typing import List, Optional
import uuid
from app.core.database import get_db
from app.models.post import Post
from app.models.user import User
from app.schemas.post import PostCreate, PostResponse
from app.dependencies.auth import get_current_user
from app.services.file_storage_service import file_storage_service

router = APIRouter(prefix="/feed", tags=["Social Feed"])

@router.post("", response_model=PostResponse)
async def create_post(
    content: str = Form(...),
    image: Optional[UploadFile] = File(None),
    db: Session = Depends(get_db), 
    current_user: User = Depends(get_current_user)
):
    try:
        media_url = None
        if image and image.size and image.size > 0:
            filename = f"{uuid.uuid4()}_{image.filename}"
            media_url = await file_storage_service.save_image(image, filename, folder="posts")

        new_post = Post(
            author_id=current_user.id,
            content=content,
            media_url=media_url
        )
        db.add(new_post)
        db.commit()
        db.refresh(new_post)
        return new_post
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

@router.get("", response_model=List[PostResponse])
def get_feed(db: Session = Depends(get_db), current_user: User = Depends(get_current_user), skip: int = 0, limit: int = 20):
    from sqlalchemy.orm import joinedload
    posts = db.query(Post).options(joinedload(Post.author)).order_by(desc(Post.created_at)).offset(skip).limit(limit).all()
    return posts
