"""
Example 'items' resource — rename / duplicate for your own domain entities.
"""

from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.item import ItemCreate, ItemRead, ItemUpdate

router = APIRouter()


@router.get("/", response_model=List[ItemRead], summary="List items")
async def list_items(skip: int = 0, limit: int = 20, db: Session = Depends(get_db)):
    """Return a paginated list of items. TODO: connect to DB."""
    return []


@router.get("/{item_id}", response_model=ItemRead, summary="Get an item")
async def get_item(item_id: int, db: Session = Depends(get_db)):
    raise HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED, detail="Not implemented yet")


@router.post("/", response_model=ItemRead, status_code=status.HTTP_201_CREATED, summary="Create item")
async def create_item(payload: ItemCreate, db: Session = Depends(get_db)):
    raise HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED, detail="Not implemented yet")


@router.patch("/{item_id}", response_model=ItemRead, summary="Update item")
async def update_item(item_id: int, payload: ItemUpdate, db: Session = Depends(get_db)):
    raise HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED, detail="Not implemented yet")


@router.delete("/{item_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Delete item")
async def delete_item(item_id: int, db: Session = Depends(get_db)):
    raise HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED, detail="Not implemented yet")
