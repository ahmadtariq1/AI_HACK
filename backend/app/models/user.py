"""
SQLAlchemy ORM model for User.
Uncomment and extend when your DB schema is ready.
"""

from sqlalchemy import Boolean, Column, Integer, String
from app.core.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    full_name = Column(String, nullable=True)
    hashed_password = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)

    # Add relationships here, e.g.:
    # items = relationship("Item", back_populates="owner")
