"""
User endpoints — CRUD placeholders.
"""

from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.user import UserCreate, UserRead, UserUpdate

router = APIRouter()


@router.get("/", response_model=List[UserRead], summary="List all users")
async def list_users(
    skip: int = 0,
    limit: int = 20,
    db: Session = Depends(get_db),
):
    """Return a paginated list of users. TODO: connect to DB."""
    # users = user_service.list(db, skip=skip, limit=limit)
    return []


@router.get("/{user_id}", response_model=UserRead, summary="Get a user by ID")
async def get_user(user_id: int, db: Session = Depends(get_db)):
    """Fetch a single user. TODO: connect to DB."""
    # user = user_service.get(db, user_id)
    # if not user:
    #     raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    raise HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED, detail="Not implemented yet")


@router.post("/", response_model=UserRead, status_code=status.HTTP_201_CREATED, summary="Create a user")
async def create_user(payload: UserCreate, db: Session = Depends(get_db)):
    """Create a new user. TODO: connect to DB."""
    # return user_service.create(db, payload)
    raise HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED, detail="Not implemented yet")


@router.patch("/{user_id}", response_model=UserRead, summary="Update a user")
async def update_user(user_id: int, payload: UserUpdate, db: Session = Depends(get_db)):
    """Partial update of a user. TODO: connect to DB."""
    raise HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED, detail="Not implemented yet")


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Delete a user")
async def delete_user(user_id: int, db: Session = Depends(get_db)):
    """Delete a user. TODO: connect to DB."""
    raise HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED, detail="Not implemented yet")
