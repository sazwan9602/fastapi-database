from typing import Optional, List
from sqlalchemy import select, desc
from sqlalchemy.orm import selectinload
from app.repositories.base import BaseRepository
from app.models.user import Post
from app.schemas.post import PostCreate, PostUpdate


class PostRepository(BaseRepository[Post, PostCreate, PostUpdate]):
    """Post-specific repositpry"""

    async def get_by_author(
        self, author_id: int, skip: int = 0, limit: int = 10
    ) -> List[Post]:
        """Get all posts by a specific author"""
        result = await self.db.execute(
            select(Post)
            .where(Post.author_id == author_id)
            .order_by(desc(Post.created_at))
            .offset(skip)
            .limit(limit)
        )

        return result.scalars().all()

    async def get_published_posts(self, skip: int = 0, limit: int = 20) -> List[Post]:
        """Get all published posts"""
        return await self.get_multi(
            skip=skip,
            limit=limit,
            filters={"published": True},
            order_by=[desc(Post.created_at)],
        )

    async def get_with_author(self, post_id: int) -> Optional[Post]:
        """Get post with author information"""
        result = await self.db.execute(
            select(Post).options(selectinload(Post.author)).where(Post.id == post_id)
        )
        return result.scalar_one_or_none()

    async def publish_post(self, post_id: int) -> Optional[Post]:
        """Publish a post"""
        return await self.update_record(post_id, {"published": True})

    async def unpublish_post(self, post_id: int) -> Optional[Post]:
        """Publish a post"""
        return await self.update_record(post_id, {"published": False})
