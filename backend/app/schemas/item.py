"""
Pydantic schemas for item request/response payloads.
Rename / extend this for your actual domain entities.
"""

from typing import Optional
from pydantic import BaseModel


class ItemBase(BaseModel):
    title: str
    description: Optional[str] = None


class ItemCreate(ItemBase):
    pass


class ItemUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None


class ItemRead(ItemBase):
    id: int

    model_config = {"from_attributes": True}
