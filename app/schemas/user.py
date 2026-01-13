from pydantic import BaseModel, EmailStr, ConfigDict
from datetime import datetime
from typing_extensions import Optional, List


# Base Schema with common attributes
class UserBase(BaseModel):
    email: EmailStr
    username: str


# schema for creata a user
class UserCreate(UserBase):
    password: str


# schema for updating a user
class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    username: Optional[str] = None
    password: Optional[str] = None
    is_active: Optional[bool] = None

# schema for user reading data
class User(UserBase):
    id: int
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

# schema with relationship
class UserWithPost(User):
    posts: List["Post"] = []

class PostBase(BaseModel):
    title: str
    content: str
    published: bool = False

class Post(PostBase):
    id: int
    created_at: datetime
    author_id: int

    model_config = ConfigDict(from_attributes=True)