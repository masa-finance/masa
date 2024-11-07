"""Base models and mixins for SQLAlchemy dataclass integration."""

from sqlalchemy.orm import DeclarativeBase, MappedAsDataclass, registry

mapper_registry = registry()

class Base(MappedAsDataclass, DeclarativeBase):
    """Base class for all SQLAlchemy models in the application.
    
    This class combines SQLAlchemy's DeclarativeBase with MappedAsDataclass to provide
    both ORM functionality and dataclass features.
    """
    registry = mapper_registry
