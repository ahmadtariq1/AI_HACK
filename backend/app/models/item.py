"""
SQLAlchemy ORM model for Item.
Rename / copy this for your actual domain entities.
"""

from sqlalchemy import Column, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from app.core.database import Base


class Item(Base):
    __tablename__ = "items"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False, index=True)
    description = Column(Text, nullable=True)

    # Uncomment when User model is ready:
    # owner_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    # owner = relationship("User", back_populates="items")
