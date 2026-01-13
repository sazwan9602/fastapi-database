from typing import Optional, List, Any, Dict
from datetime import datetime, UTC
from sqlalchemy import select
from app.repositories.base import (
    BaseRepository,
    ModelType,
    CreateSchemaType,
    UpdateSchemaType,
)


class SoftDeleteRepository(
    BaseRepository[ModelType, CreateSchemaType, UpdateSchemaType]
):
    """Repository with soft delete fucntionality"""

    async def get(self, id: Any, include_deleted: bool = False) -> Optional[ModelType]:
        """Get record, optionally including soft deleted ones"""
        query = select(self.model).where(self.model.id == id)

        if not include_deleted and hasattr(self.model, "deleted_at"):
            query = query.where(self.model.deleted_at.is_(None))

        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def get_multi(
        self,
        *,
        skip: int = 0,
        limit: int = 100,
        filters: Optional[Dict[str, Any]] = None,
        order_by: Optional[List[Any]] = None,
        include_deleted: bool = False,
    ):
        """Get multiple records, optionally including soft deleted ones"""
        query = select(self.model)

        # Exclude soft deleted by default
        if not include_deleted and hasattr(self.model, "deleted_at"):
            query = query.where(self.model.deleted_at.is_(None))

        if filters:
            for field, value in filters.items():
                if hasattr(self.model, field):
                    query = query.where(getattr(self.model, field) == value)

        if order_by:
            query = query.order_by(*order_by)

        query = query.offset(skip).limit(limit)

        result = await self.db.execute(query)
        return result.scalars().all()

    async def soft_delete(self, id: Any) -> bool:
        """Soft delete a record by setting deleted_at timestamp"""
        if not hasattr(self.model, "deleted_at"):
            raise ValueError(f"{self.model.__name__} does not support soft delete")

        db_obj = await self.get(id)
        if not db_obj:
            return False

        db_obj.deleted_at = datetime.now(tz=UTC)
        # self.db.add(db_obj)
        await self.db.commit()
        return True

    async def restore(self, id: Any) -> Optional[ModelType]:
        """Restore a soft deleted record"""
        if not hasattr(self.model, "deleted_at"):
            raise ValueError(f"{self.model.__name__} does not support soft delete")

        db_obj = await self.get(id, include_deleted=True)
        if not db_obj or db_obj.deleted_at is None:
            return None

        db_obj.deleted_at = None
        # self.db.add(db_obj)
        await self.db.commit()
        await self.db.refresh(db_obj)
        return db_obj

    async def permanent_delete(self, id: Any) -> bool:
        """Permanently delete a record (hard delete)"""
        return await super().delete_record(id)
