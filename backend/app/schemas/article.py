"""Article metadata Pydantic schemas."""
from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class ArticleMetadataCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=1024)
    abstract: str | None = None
    authors: list[str] | None = None
    doi: str | None = Field(None, max_length=255)
    source: str | None = Field(None, max_length=255)
    published_at: datetime | None = None
    keywords: list[str] | None = None
    raw_metadata: dict[str, Any] | None = None


class ArticleMetadataUpdate(BaseModel):
    title: str | None = Field(None, min_length=1, max_length=1024)
    abstract: str | None = None
    authors: list[str] | None = None
    doi: str | None = Field(None, max_length=255)
    source: str | None = Field(None, max_length=255)
    published_at: datetime | None = None
    keywords: list[str] | None = None
    raw_metadata: dict[str, Any] | None = None


class ArticleMetadataResponse(BaseModel):
    id: str
    title: str
    abstract: str | None
    authors: list[str] | dict | None
    doi: str | None
    source: str | None
    published_at: datetime | None
    keywords: list[str] | None
    raw_metadata: dict[str, Any] | None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class ArticleListParams(BaseModel):
    skip: int = Field(0, ge=0, description="Offset for pagination")
    limit: int = Field(20, ge=1, le=100, description="Page size")
    search: str | None = Field(None, max_length=500)
    source: str | None = Field(None, max_length=255)
    sort: str = Field("created_at", pattern="^(created_at|published_at|title)$")
    order: str = Field("desc", pattern="^(asc|desc)$")
