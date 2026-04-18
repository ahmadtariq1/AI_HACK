"""
Shared utility helpers.
"""

import uuid
from datetime import datetime, timezone


def utcnow() -> datetime:
    """Return current UTC datetime (timezone-aware)."""
    return datetime.now(timezone.utc)


def new_uuid() -> str:
    """Generate a new UUID4 string."""
    return str(uuid.uuid4())


def paginate(total: int, skip: int, limit: int) -> dict:
    """Build a pagination metadata dict."""
    return {
        "total": total,
        "skip": skip,
        "limit": limit,
        "has_more": (skip + limit) < total,
    }
