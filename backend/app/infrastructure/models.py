"""SQLAlchemy ORM models."""
from datetime import datetime
from uuid import uuid4

from sqlalchemy import DateTime, Enum, ForeignKey, Index, String, Text, func
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.domain.enums import UserRole
from app.infrastructure.base import Base


def generate_uuid() -> str:
    return str(uuid4())


class UserModel(Base):
    __tablename__ = "users"

    id: Mapped[str] = mapped_column(UUID(as_uuid=False), primary_key=True, default=generate_uuid)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    full_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    role: Mapped[UserRole] = mapped_column(Enum(UserRole), default=UserRole.USER, nullable=False)
    is_active: Mapped[bool] = mapped_column(default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    articles = relationship("ArticleMetadataModel", back_populates="created_by_user", lazy="selectin")


class ArticleMetadataModel(Base):
    __tablename__ = "article_metadata"

    id: Mapped[str] = mapped_column(UUID(as_uuid=False), primary_key=True, default=generate_uuid)
    title: Mapped[str] = mapped_column(String(1024), nullable=False, index=True)
    abstract: Mapped[str | None] = mapped_column(Text, nullable=True)
    authors: Mapped[dict | list | None] = mapped_column(JSONB, nullable=True)  # ["Author 1", "Author 2"]
    doi: Mapped[str | None] = mapped_column(String(255), unique=True, index=True, nullable=True)
    source: Mapped[str | None] = mapped_column(String(255), nullable=True, index=True)  # journal/conference
    published_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True, index=True)
    keywords: Mapped[list | None] = mapped_column(JSONB, nullable=True)  # ["keyword1", "keyword2"]
    raw_metadata: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    created_by_id: Mapped[str | None] = mapped_column(UUID(as_uuid=False), ForeignKey("users.id"), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    created_by_user = relationship("UserModel", back_populates="articles", lazy="selectin")
