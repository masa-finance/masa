"""Base models and mixins for SQLAlchemy dataclass integration."""

from dataclasses import dataclass
from datetime import datetime
from sqlalchemy.orm import DeclarativeBase, MappedAsDataclass

@dataclass
class Base(MappedAsDataclass, DeclarativeBase):
    """Base class for all SQLAlchemy models using dataclass integration.
    
    Attributes:
        created_at (datetime): Timestamp when record was created
        updated_at (datetime): Timestamp when record was last updated
    """
    
    created_at: datetime = datetime.utcnow()
    updated_at: datetime = datetime.utcnow()
