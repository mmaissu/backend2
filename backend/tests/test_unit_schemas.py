from datetime import datetime, timezone

import pytest
from pydantic import ValidationError

from app.schemas.article import (
    ArticleListParams,
    ArticleMetadataCreate,
    ArticleMetadataResponse,
    ArticleMetadataUpdate,
)
from app.schemas.common import PaginatedResponse


def test_article_metadata_create_validates_title_min_length():
    with pytest.raises(ValidationError):
        ArticleMetadataCreate(title="")


def test_article_metadata_update_allows_partial():
    obj = ArticleMetadataUpdate(title="New title")
    assert obj.title == "New title"


def test_article_list_params_valid_defaults_and_patterns():
    params = ArticleListParams()
    assert params.skip == 0
    assert params.limit == 20
    assert params.sort == "created_at"
    assert params.order == "desc"

    with pytest.raises(ValidationError):
        ArticleListParams(sort="invalid")

    with pytest.raises(ValidationError):
        ArticleListParams(order="up")


def test_article_metadata_response_from_attributes_like_shape():
    now = datetime.now(timezone.utc)
    payload = {
        "id": "1",
        "title": "T",
        "abstract": None,
        "authors": ["A"],
        "doi": None,
        "source": None,
        "published_at": None,
        "keywords": None,
        "raw_metadata": {"x": 1},
        "created_at": now,
        "updated_at": now,
    }
    resp = ArticleMetadataResponse(**payload)
    assert resp.id == "1"
    assert resp.raw_metadata == {"x": 1}


def test_paginated_response_basic():
    resp = PaginatedResponse[int](items=[1, 2], total=2, skip=0, limit=10)
    assert resp.items == [1, 2]
    assert resp.total == 2

