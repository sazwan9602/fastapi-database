from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from app.database import get_db
from app.schemas.post import Post, PostCreate, PostUpdate, PostWithAuthor
from app.repositories.post import PostRepository
from app.repositories.user import UserRepository
from app.models.user import Post as PostModel, User as UserModel

router = APIRouter(prefix="/posts", tags=["posts"])


def get_post_repository(db: AsyncSession = Depends(get_db)) -> PostRepository:
    return PostRepository(model=PostModel, db=db)


def get_user_repository(db: AsyncSession = Depends(get_db)) -> UserRepository:
    return UserRepository(model=UserModel, db=db)


@router.post("/", response_model=Post, status_code=status.HTTP_201_CREATED)
async def create_post(
    post: PostCreate,
    post_repo: PostRepository = Depends(get_post_repository),
    user_repo: UserRepository = Depends(get_user_repository),
):
    # verify author exists
    author = await user_repo.get(post.author_id)
    if not author:
        raise HTTPException(status_code=404, detail="Author not found")
    return await post_repo.create_record(post)


@router.get("/", response_model=List[Post])
async def read_posts(
    skip: int = 0,
    limit: int = 20,
    published_only: bool = True,
    repo: PostRepository = Depends(get_post_repository),
):
    if published_only:
        return await repo.get_published_posts(skip=skip, limit=limit)
    return await repo.get_multi(skip=skip, limit=limit)


@router.get("/{post_id}", response_model=PostWithAuthor)
async def read_post(
    post_id: int,
    repo: PostRepository = Depends(get_post_repository),
):
    post = await repo.get_with_author(post_id)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")

    return post


@router.get("/author/{author_id}", response_model=List[Post])
async def get_posts_by_author(
    author_id: int,
    skip: int = 0,
    limit: int = 10,
    repo: PostRepository = Depends(get_post_repository),
):
    return await repo.get_by_author(author_id, skip=skip, limit=limit)


@router.put("/{post_id}", response_model=Post)
async def update_post(
    post_id: int, post: PostUpdate, repo: PostRepository = Depends(get_post_repository)
):
    updated_post = await repo.update_record(post_id, post)
    if not updated_post:
        raise HTTPException(status_code=404, detail="Post not found")
    return updated_post


@router.post("/{post_id}/publish", response_model=Post)
async def publish_post(
    post_id: int, repo: PostRepository = Depends(get_post_repository)
):
    post = await repo.publish_post(post_id)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    return post


@router.post("/{post_id}un/publish", response_model=Post)
async def unpublish_post(
    post_id: int, repo: PostRepository = Depends(get_post_repository)
):
    post = await repo.unpublish_post(post_id)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    return post


@router.delete("/{post_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_post(
    post_id: int, repo: PostRepository = Depends(get_post_repository)
):
    success = await repo.delete_record(post_id)
    if not success:
        raise HTTPException(status_code=404, detail="Post not found")
