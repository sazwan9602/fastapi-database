from typing import Generic, TypeVar, Type, Optional, List, Any, Dict
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete, func
from app.database import Base
from pydantic import BaseModel

ModelType = TypeVar("ModelType", bound=Base)
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)


class BaseRepository(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    """Base repository with common CRUD operations"""

    def __init__(self, model: Type[ModelType], db: AsyncSession):
        self.model = model
        self.db = db

    async def get(self, id: Any) -> Optional[ModelType]:
        """Get a single record by ID"""
        result = await self.db.execute(select(self.model).where(self.model.id == id))
        return result.scalar_one_or_none()

    async def get_multi(
        self,
        *,
        skip: int = 0,
        limit: int = 100,
        filters: Optional[Dict[str, Any]] = None,
        order_by: Optional[List[Any]] = None,
    ) -> List[ModelType]:
        """Get multiple records with filtering and pagination"""
        query = select(self.model)

        # apply filters
        if filters:
            for field, value in filters.items():
                if hasattr(self.model, field):
                    query = query.where(getattr(self.model, field) == value)

        # apply ordering
        if order_by:
            query = query.order_by(*order_by)

        # apply pagination
        query = query.offset(skip).limit(limit)

        result = await self.db.execute(query)
        return result.scalars().all()

    async def get_all(self) -> List[ModelType]:
        """Get all records"""
        result = await self.db.execute(select(self.model))
        return result.scalars().all()

    async def create_record(self, obj_in: CreateSchemaType) -> ModelType:
        """Createa a new record"""
        obj_data = obj_in.model_dump()
        db_obj = self.model(**obj_data)
        self.db.add(db_obj)
        await self.db.commit()
        await self.db.refresh(db_obj)
        return db_obj

    async def update_record(
        self, id: Any, obj_in: UpdateSchemaType | Dict[str, Any]
    ) -> Optional[ModelType]:
        """Update existing record"""
        db_obj = await self.get(id)
        if not db_obj:
            return None

        # convert pydantic model to dict if necessary
        if isinstance(obj_in, BaseModel):
            update_data = obj_in.model_dump(exclude_unset=True)
        else:
            update_data = obj_in

        # update fields
        for field, value in update_data.items():
            if hasattr(db_obj, field):
                setattr(db_obj, field, value)

        await self.db.commit()
        await self.db.refresh(db_obj)
        return db_obj

    async def delete_record(self, id: Any) -> bool:
        """Delete a record"""
        db_obj = await self.get(id)
        if not db_obj:
            return False

        await self.db.delete(db_obj)
        await self.db.commit()
        return True

    async def count(self, filters: Optional[Dict[str, Any]] = None) -> int:
        """Count record with optimal filters"""
        query = select(func.count()).select_from(self.model)

        if filters:
            for field, value in filters.items():
                if hasattr(self.model, field):
                    query = query.where(getattr(self.model, field) == value)
        result = await self.db.execute(query)
        return result.scalar()

    async def exists(self, id: Any) -> bool:
        """Check if record exist"""
        result = await self.db.execute(select(self.model.id).where(self.model.id == id))
        return result.scalar_one_or_none() is not None

    async def bulk_create(self, objs_in: List[CreateSchemaType]) -> List[ModelType]:
        """Create multiple records at once"""
        db_objs = [self.model(**obj.model_dump()) for obj in objs_in]
        self.db.add_all(db_objs)
        await self.db.commit()

        # refresh all objects
        for db_obj in db_objs:
            await self.db.refresh(db_obj)
        return db_objs

    async def bulk_update(self, updates: List[Dict[str, Any]]) -> int:
        """Bulk update records. Each dict should contain id and fields to update"""
        if not updates:
            return 0

        for update_data in updates:
            id = update_data.pop("id")
            await self.db.execute(
                update(self.model).where(self.model.id == id).values(**update_data)
            )

        await self.db.commit()
        return len(updates)

    async def bulk_delete(self, ids: List[Any]) -> int:
        """Delete multiple records by Ids"""
        if not ids:
            return 0

        result = await self.db.execute(delete(self.model).where(self.model.id.in_(ids)))
        await self.db.commit()
        return result.rowcount
