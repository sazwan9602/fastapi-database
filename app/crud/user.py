from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from typing_extensions import Optional, List
from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate


async def get_user(db: AsyncSession, user_id: int) -> Optional[User]:
    result = await db.execute(select(User).where(User.id == user_id))
    return result.scalar_one_or_none()


async def get_user_by_email(db: AsyncSession, email: str) -> Optional[User]:
    result = await db.execute(select(User).where(User.email == email))
    return result.scalar_one_or_none()


async def get_users(db: AsyncSession, skip: int = 0, limit: int = 100) -> List[User]:
    result = await db.execute(select(User).offset(skip).limit(limit))
    return result.scalars().all()


async def create_user(db: AsyncSession, user: UserCreate) -> User:
    fake_hashed_password = user.password + "_hashed"

    db_user = User(
        email=user.email, username=user.username, hashed_password=fake_hashed_password
    )

    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)
    return db_user


async def update_user(
    db: AsyncSession, user_id: int, user_update: UserUpdate
) -> Optional[User]:
    result = await db.execute(select(User).where(User.id == user_id))
    db_user = result.scalar_one_or_none()

    if not db_user:
        return None

    # update only provided data
    update_data = user_update.model_dump(exclude_unset=True)

    if "password" in update_data:
        update_data["hashed_password"] = update_data.pop("password") + "_hashed"

    for field, value in update_data.items():
        setattr(db_user, field, value)

    await db.commit()
    await db.refresh(db_user)
    return db_user


async def delete_user(db: AsyncSession, user_id: int) -> bool:
    result = await db.execute(select(User).where(User.id == user_id))

    db_user = result.scalar_one_or_none()
    if not db_user:
        return False

    await db.delete(db_user)
    await db.commit()
    return True


# get user with relationships
async def get_user_with_posts(db: AsyncSession, user_id: int) -> Optional[User]:
    result = await db.execute(
        select(User).options(selectinload(User.posts)).where(User.id == user_id)
    )
    return result.scalar_one_or_none()
