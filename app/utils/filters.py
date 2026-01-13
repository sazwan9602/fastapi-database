from typing import Optional, Any, Dict
from pydantic import BaseModel
from datetime import datetime


class UserFilter(BaseModel):
    """Advanced filtering for users"""

    is_active: Optional[bool] = None
    created_after: Optional[datetime] = None
    created_before: Optional[datetime] = None
    email_contains: Optional[str] = None
    username_contains: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for repository"""
        filters = {}
        if self.is_active is not None:
            filters["is_active"] = self.is_active
        return filters
