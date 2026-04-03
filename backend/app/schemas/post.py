from typing import Optional, List
from pydantic import BaseModel
from datetime import datetime

class PostAuthor(BaseModel):
    id: int
    name: str
    title: Optional[str] = None
    avatar_url: Optional[str] = None

    class Config:
        from_attributes = True

class PostBase(BaseModel):
    content: str
    media_url: Optional[str] = None

class PostCreate(PostBase):
    pass

class PostResponse(PostBase):
    id: int
    author_id: int
    created_at: datetime
    likes_count: int
    author: PostAuthor

    class Config:
        from_attributes = True
