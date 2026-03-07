"""Articles CRUD API with search, filter, pagination."""
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import and_, func, or_, select, true
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import get_current_user, get_current_user_optional
from app.domain.enums import UserRole
from app.infrastructure.database import get_db
from app.infrastructure.models import ArticleMetadataModel, UserModel
from app.schemas.article import (
    ArticleListParams,
    ArticleMetadataCreate,
    ArticleMetadataResponse,
    ArticleMetadataUpdate,
)
from app.schemas.common import PaginatedResponse

router = APIRouter()


def _filter_criteria(params: ArticleListParams, created_by_id: str | None = None):
    """Build filter expressions for reuse in count and list queries (SQL parameterized — no SQLi)."""
    criteria = []
    if params.search:
        search = f"%{params.search}%"
        criteria.append(
            or_(
                ArticleMetadataModel.title.ilike(search),
                ArticleMetadataModel.abstract.ilike(search),
            )
        )
    if params.source:
        criteria.append(ArticleMetadataModel.source == params.source)
    if created_by_id:
        criteria.append(ArticleMetadataModel.created_by_id == created_by_id)
    return and_(*criteria) if criteria else true()


def _apply_sort(q, params: ArticleListParams):
    sort_col = getattr(ArticleMetadataModel, params.sort, ArticleMetadataModel.created_at)
    return q.order_by(sort_col.desc() if params.order == "desc" else sort_col.asc())


@router.get("", response_model=PaginatedResponse[ArticleMetadataResponse])
async def list_articles(
    db: AsyncSession = Depends(get_db),
    current_user: UserModel | None = Depends(get_current_user_optional),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    search: str | None = Query(None, max_length=500),
    source: str | None = Query(None, max_length=255),
    mine: bool = Query(False, description="Only my articles"),
    sort: str = Query("created_at", pattern="^(created_at|published_at|title)$"),
    order: str = Query("desc", pattern="^(asc|desc)$"),
):
    if mine and not current_user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")
    created_by_id = str(current_user.id) if mine and current_user else None
    params = ArticleListParams(skip=skip, limit=limit, search=search, source=source, sort=sort, order=order)
    criteria = _filter_criteria(params, created_by_id=created_by_id)
    count_q = select(func.count()).select_from(ArticleMetadataModel).where(criteria)
    total_result = await db.execute(count_q)
    total = total_result.scalar() or 0
    q = select(ArticleMetadataModel).where(criteria)
    q = _apply_sort(q, params)
    q = q.offset(params.skip).limit(params.limit)
    result = await db.execute(q)
    items = result.scalars().all()
    return PaginatedResponse(items=items, total=total, skip=params.skip, limit=params.limit)


@router.get("/{article_id}", response_model=ArticleMetadataResponse)
async def get_article(
    article_id: str,
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(ArticleMetadataModel).where(ArticleMetadataModel.id == article_id))
    article = result.scalar_one_or_none()
    if not article:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Article not found")
    return article


@router.post("", response_model=ArticleMetadataResponse, status_code=status.HTTP_201_CREATED)
async def create_article(
    body: ArticleMetadataCreate,
    db: AsyncSession = Depends(get_db),
    current_user: UserModel = Depends(get_current_user),
):
    article = ArticleMetadataModel(**body.model_dump(), created_by_id=str(current_user.id))
    db.add(article)
    await db.flush()
    await db.refresh(article)
    return article


@router.patch("/{article_id}", response_model=ArticleMetadataResponse)
async def update_article(
    article_id: str,
    body: ArticleMetadataUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: UserModel = Depends(get_current_user),
):
    result = await db.execute(select(ArticleMetadataModel).where(ArticleMetadataModel.id == article_id))
    article = result.scalar_one_or_none()
    if not article:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Article not found")
    if article.created_by_id != str(current_user.id) and current_user.role != UserRole.ADMIN:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not allowed to update this article")
    data = body.model_dump(exclude_unset=True)
    for k, v in data.items():
        setattr(article, k, v)
    await db.flush()
    await db.refresh(article)
    return article


@router.delete("/{article_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_article(
    article_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: UserModel = Depends(get_current_user),
):
    result = await db.execute(select(ArticleMetadataModel).where(ArticleMetadataModel.id == article_id))
    article = result.scalar_one_or_none()
    if not article:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Article not found")
    if article.created_by_id != str(current_user.id) and current_user.role != UserRole.ADMIN:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not allowed to delete this article")
    await db.delete(article)
    return None
