from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing_extensions import List
from app.database import get_db
from app.schemas.user import User, UserCreate, UserUpdate, UserWithPost
from app.repositories.user import UserRepository
from app.utils.pagination import PaginationParams, PageResponse
# from app.crud import user as crud_user


router = APIRouter(prefix="/users", tags=["users"])


def get_user_repository(db: AsyncSession = Depends(get_db)) -> UserRepository:
    return UserRepository(model=User, db=db)


@router.post("/", response_model=User, status_code=status.HTTP_201_CREATED)
async def create_user(
    user: UserCreate, repo: UserRepository = Depends(get_user_repository)
):
    # check email exists
    if await repo.email_exists(user.email):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered."
        )
    # check if username exists
    if await repo.username_exists(user.username):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Username already taken."
        )
    return repo.create_record(user)


@router.get("/", response_model=PageResponse[User])
async def read_users(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    repo: UserRepository = Depends(get_user_repository),
):
    pagination = PaginationParams(page=page, page_size=page_size)

    users = await repo.get_multi(skip=pagination.skip, limit=pagination.limit)

    total = await repo.count()

    return PageResponse.create(items=users, total=total, page=page, page_size=page_size)


@router.get("/search", response_model=List[User])
async def search_users(
    q: str = Query(..., min_length=2),
    skip: int = 0,
    limit: int = 20,
    repo: UserRepository = Depends(get_user_repository),
):
    return await repo.search_users(query=q, skip=skip, limit=limit)


@router.get("/active", response_model=List[User])
async def get_active_users(
    skip: int = 0, limit: int = 100, repo: UserRepository = Depends(get_user_repository)
):
    return await repo.get_active_users(skip=skip, limit=limit)


@router.get("/stats", response_model=dict)
async def get_user_stats(repo: UserRepository = Depends(get_user_repository)):
    counts = await repo.count_by_status()
    total = await repo.count()
    return {"total": total, **counts}


@router.get("/{user_id}", response_model=User)
async def read_user(user_id: int, repo: UserRepository = Depends(get_user_repository)):
    user = await repo.get(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")


@router.get("/{user_id}/posts", response_model=UserWithPost)
async def read_user_with_posts(
    user_id: int, repo: UserRepository = Depends(get_user_repository)
):
    user = await repo.get_with_posts(user_id)

    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.put("/{user_id}", response_model=User)
async def update_user(
    user_id: int, user: UserUpdate, repo: UserRepository = Depends(get_user_repository)
):
    # validate email uniqueness fi updating
    if user.email and await repo.email_exists(user.email, execlude_id=user_id):
        raise HTTPException(status_code=400, detail="Email already in use")

    # validate username uniqueness if updating
    if user.username and await repo.username_exists(user.username, exclude_id=user_id):
        raise HTTPException(status_code=400, detail="Username already taken")

    updated_user = await repo.update_record(user_id, user)
    if not updated_user:
        raise HTTPException(status_code=404, detail="user not found")
    return updated_user


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def soft_delete_user(
    user_id: int, repo: UserRepository = Depends(get_user_repository)
):
    success = await repo.soft_delete(user_id)
    if not success:
        raise HTTPException(status_code=404, detail="User not found")


@router.post("/{user_id}/restore", response_model=User)
async def restore_user(
    user_id: int, repo: UserRepository = Depends(get_user_repository)
):
    user = await repo.restore(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found or deleted")
    return user


@router.delete("/{user_id}/permanent", status_code=status.HTTP_204_NO_CONTENT)
async def permanent_delete_user(
    user_id: int, repo: UserRepository = Depends(get_user_repository)
):
    success = await repo.permanent_delete(user_id)
    if not success:
        raise HTTPException(status_code=404, detail="User not found")


# @router.post("/", response_model=User, status_code=status.HTTP_201_CREATED, deprecated=True)
# async def create_user(user: UserCreate, db: AsyncSession = Depends(get_db)):
#     db_user = await crud_user.get_user_by_email(db, email=user.email)
#     if db_user:
#         raise HTTPException(
#             status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered."
#         )
#     return await crud_user.create_user(db=db, user=user)


# @router.get("/", response_model=List[User])
# async def read_users(skip: int, limit: int, db: AsyncSession = Depends(get_db)):
#     users = await crud_user.get_users(db=db, skip=skip, limit=limit)
#     return users


# @router.get("/{user_id}", response_model=User)
# async def read_user(user_id: int, db: AsyncSession = Depends(get_db)):
#     db_user = await crud_user.get_user(db, user_id)
#     if db_user is None:
#         raise HTTPException(status_code=404, detail="User not found")
#     return db_user


# @router.get("/{user_id}/posts", response_model=UserWithPost)
# async def read_user_with_posts(user_id: int, db: AsyncSession = Depends(get_db)):
#     db_user = await crud_user.get_user_with_posts(db=db, user_id=user_id)
#     if db_user is None:
#         raise HTTPException(status_code=404, detail="User not found")
#     return db_user


# @router.put("/{user_id}", response_model=User)
# async def update_user(
#     user_id: int, user: UserUpdate, db: AsyncSession = Depends(get_db)
# ):
#     db_user = await crud_user.update_user(db=db, user_id=user_id, user_update=user)
#     if db_user is None:
#         raise HTTPException(status_code=404, detail="User not found")
#     return db_user


# @router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
# async def delete_user(user_id: int, db: AsyncSession = Depends(get_db)):
#     success = await crud_user.delete_user(db=db, user_id=user_id)
#     if not success:
#         raise HTTPException(status_code=404, detail="User not found")
