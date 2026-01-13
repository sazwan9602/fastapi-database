from typing import Optional, List
from sqlalchemy import select, or_, and_, func
from sqlalchemy.orm import selectinload
from app.repositories.soft_delete_base import SoftDeleteRepository
from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate
from datetime import timedelta, datetime, UTC


class UserRepository(SoftDeleteRepository[User, UserCreate, UserUpdate]):
    """User-specific repository with custom queries"""

    async def get_by_email(self, email: str) -> Optional[User]:
        """Get user by email"""
        result = await self.db.execute(
            select(User).where(User.email == email).where(User.deleted_at.is_(None))
        )
        return result.scalar_one_or_none()

    async def get_by_username(self, username: str) -> Optional[User]:
        """Get user with all their posts (eager loading)"""
        result = await self.db.execute(
            select(User)
            .where(User.username == username)
            .where(User.deleted_at.is_(None))
        )
        return result.scalar_one_or_none()

    async def get_with_posts(self, user_id: int) -> Optional[User]:
        """Get user with all their posts (eager loading)"""
        result = await self.db.execute(
            select(User)
            .options(selectinload(User.posts))
            .where(User.id == user_id)
            .where(User.deleted_at.is_(None))
        )
        return result.scalar_one_or_none()

    async def search_users(
        self, query: str, skip: int = 0, limit: int = 20
    ) -> List[User]:
        """Search users by username or email"""
        search_pattern = f"%{query}%"
        result = await self.db.execute(
            select(User)
            .where(
                and_(
                    or_(
                        User.username.ilike(search_pattern),
                        User.email.ilike(search_pattern),
                    ),
                    User.deleted_at.is_(None),
                )
            )
            .offset(skip)
            .limit(limit)
        )
        return result.scalars().all()

    async def get_active_users(self, skip: int = 0, limit: int = 100) -> List[User]:
        """Get only active users"""
        return await self.get_multi(skip=skip, limit=limit, filters={"is_active": True})

    async def count_by_status(self) -> dict:
        """count users by active status"""
        result = await self.db.execute(
            select(User.is_active, func.count(User.id).label("count"))
            .where(User.deleted_at.id_(None))
            .group_by(User.is_active)
        )

        counts = {"active": 0, "inactive": 0}
        for row in result:
            if row.is_active:
                counts["active"] = row.count
            else:
                counts["inactive"] = row.count

        return counts

    async def get_recent_users(self, days: int = 7, limit: int = 10) -> List[User]:
        """Get recently created users"""
        cutoff_date = datetime.now(tz=UTC) - timedelta(days=days)

        result = await self.db.execute(
            select(User)
            .where(User.created_at >= cutoff_date)
            .where(User.deleted_at.is_(None))
            .order_by(User.created_at.desc())
            .limit(limit)
        )

        return result.scalars().all()

    async def email_exists(self, email: str, execlude_id: Optional[int] = None) -> bool:
        """check if email exists (useful for validation)"""
        query = select(User.id).where(User.email == email)
        if execlude_id:
            query = query.where(User.id != execlude_id)

        result = await self.db.execute(query)
        return result.scalar_one_or_none() is not None

    async def username_exists(
        self, username: str, exclude_id: Optional[int] = None
    ) -> bool:
        """check if username exists"""
        query = select(User.id).where(User.username == username)

        if exclude_id:
            query = query.where(User.id != exclude_id)

        result = await self.db.execute(query)
        return result.scalar_one_or_none is not None
