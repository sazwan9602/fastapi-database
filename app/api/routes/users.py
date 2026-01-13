from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing_extensions import List
from app.database import get_db
from app.schemas.user import User, UserCreate, UserUpdate, UserWithPost
from app.crud import user as crud_user


router = APIRouter(prefix="/users", tags=["users"])


@router.post("/", response_model=User, status_code=status.HTTP_201_CREATED)
async def create_user(user: UserCreate, db: AsyncSession = Depends(get_db)):
    db_user = await crud_user.get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered."
        )
    return await crud_user.create_user(db=db, user=user)


@router.get("/", response_model=List[User])
async def read_users(skip: int, limit: int, db: AsyncSession = Depends(get_db)):
    users = await crud_user.get_users(db=db, skip=skip, limit=limit)
    return users


@router.get("/{user_id}", response_model=User)
async def read_user(user_id: int, db: AsyncSession = Depends(get_db)):
    db_user = await crud_user.get_user(db, user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user


@router.get("/{user_id}/posts", response_model=UserWithPost)
async def read_user_with_posts(user_id: int, db: AsyncSession = Depends(get_db)):
    db_user = await crud_user.get_user_with_posts(db=db, user_id=user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user


@router.put("/{user_id}", response_model=User)
async def update_user(
    user_id: int, user: UserUpdate, db: AsyncSession = Depends(get_db)
):
    db_user = await crud_user.update_user(db=db, user_id=user_id, user_update=user)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(user_id: int, db: AsyncSession = Depends(get_db)):
    success = await crud_user.delete_user(db=db, user_id=user_id)
    if not success:
        raise HTTPException(status_code=404, detail="User not found")
