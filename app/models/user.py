from sqlalchemy import String, Boolean, DateTime, ForeignKey, Table, Column, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime, UTC
from typing_extensions import List, Optional
from app.database import Base

# many to many association table
user_roles = Table(
    "user_roles",
    Base.metadata,
    Column("user_id", ForeignKey("users.id"), primary_key=True),
    Column("role_id", ForeignKey("roles.id"), primary_key=True),
)


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(
        String(255), unique=True, index=True, nullable=False
    )
    username: Mapped[str] = mapped_column(
        String(50), unique=True, index=True, nullable=False
    )
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )
    # one-to-many relationship
    posts: Mapped[List["Post"]] = relationship(
        "Post", back_populates="author", cascade="all, delete-orphan"
    )  # delete posts if user deleted
    # many-to-many relationship
    roles: Mapped[List["Role"]] = relationship(
        "Role", secondary=user_roles, back_populates="users"
    )  # secondary: only many to many needed


class Post(Base):
    __tablename__ = "posts"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    published: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )  # foreign key
    author_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    # relationship
    author: Mapped["User"] = relationship("User", back_populates="posts")


class Role(Base):
    __tablename__ = "roles"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    description: Mapped[Optional[str]] = mapped_column(String(255))
    # many to many relationship
    users: Mapped[List["User"]] = relationship(
        "User", secondary=user_roles, back_populates="roles"
    )
