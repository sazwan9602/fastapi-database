from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import Optional
from app.schemas.user import User


class PostBase(BaseModel):
    title: str
    content: str
    published: bool = False


class PostCreate(PostBase):
    author_id: int


class PostUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
    published: Optional[bool] = None


class Post(PostBase):
    id: int
    author_id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class PostWithAuthor(Post):
    author: "User"

PostWithAuthor.model_rebuild()
