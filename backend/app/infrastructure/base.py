"""SQLAlchemy declarative base (avoids circular import with database.py and models.py)."""
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """Base class for all ORM models."""
