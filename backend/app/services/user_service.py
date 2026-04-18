"""
User service layer — business logic between routes and DB.
Extend with your actual queries when the model is ready.
"""

from typing import List, Optional

from sqlalchemy.orm import Session

from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate
from app.core.security import get_password_hash


def get(db: Session, user_id: int) -> Optional[User]:
    return db.query(User).filter(User.id == user_id).first()


def get_by_email(db: Session, email: str) -> Optional[User]:
    return db.query(User).filter(User.email == email).first()


def list_users(db: Session, skip: int = 0, limit: int = 20) -> List[User]:
    return db.query(User).offset(skip).limit(limit).all()


def create(db: Session, payload: UserCreate) -> User:
    db_user = User(
        email=payload.email,
        full_name=payload.full_name,
        hashed_password=get_password_hash(payload.password),
        is_active=payload.is_active,
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def update(db: Session, user_id: int, payload: UserUpdate) -> Optional[User]:
    db_user = get(db, user_id)
    if not db_user:
        return None
    update_data = payload.model_dump(exclude_unset=True)
    if "password" in update_data:
        update_data["hashed_password"] = get_password_hash(update_data.pop("password"))
    for field, value in update_data.items():
        setattr(db_user, field, value)
    db.commit()
    db.refresh(db_user)
    return db_user


def delete(db: Session, user_id: int) -> bool:
    db_user = get(db, user_id)
    if not db_user:
        return False
    db.delete(db_user)
    db.commit()
    return True
