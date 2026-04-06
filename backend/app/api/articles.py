from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import asc, desc, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.infrastructure.database import get_db
from app.infrastructure.models import ArticleMetadataModel

router = APIRouter()


@router.get("")
async def get_articles(
    db: AsyncSession = Depends(get_db),
    search: str | None = Query(default=None),
    only_with_doi: bool = Query(default=False),
    sort_by: str = Query(default="newest"),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=6, ge=1, le=50),
):
    query = select(ArticleMetadataModel)

    if search:
        search_pattern = f"%{search.lower()}%"
        query = query.where(
            func.lower(ArticleMetadataModel.title).like(search_pattern)
            | func.lower(func.coalesce(ArticleMetadataModel.source, "")).like(search_pattern)
            | func.lower(func.coalesce(ArticleMetadataModel.doi, "")).like(search_pattern)
        )

    if only_with_doi:
        query = query.where(ArticleMetadataModel.doi.is_not(None))

    if sort_by == "oldest":
        query = query.order_by(asc(ArticleMetadataModel.created_at))
    elif sort_by == "most_cited":
        query = query.order_by(desc(func.coalesce(ArticleMetadataModel.cited_by_count, 0)))
    elif sort_by == "least_cited":
        query = query.order_by(asc(func.coalesce(ArticleMetadataModel.cited_by_count, 0)))
    elif sort_by == "title_asc":
        query = query.order_by(asc(ArticleMetadataModel.title))
    elif sort_by == "title_desc":
        query = query.order_by(desc(ArticleMetadataModel.title))
    else:
        query = query.order_by(desc(ArticleMetadataModel.created_at))

    count_query = select(func.count()).select_from(query.subquery())
    total_items = await db.scalar(count_query)
    total_items = total_items or 0

    offset = (page - 1) * page_size
    query = query.offset(offset).limit(page_size)

    result = await db.execute(query)
    articles = result.scalars().all()

    total_pages = (total_items + page_size - 1) // page_size if total_items > 0 else 1

    return {
        "items": [
            {
                "id": article.id,
                "title": article.title,
                "abstract": article.abstract,
                "authors": article.authors,
                "doi": article.doi,
                "source": article.source,
                "cited_by_count": article.cited_by_count,
            }
            for article in articles
        ],
        "pagination": {
            "page": page,
            "page_size": page_size,
            "total_items": total_items,
            "total_pages": total_pages,
        },
    }


@router.delete("/{article_id}")
async def delete_article(article_id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(ArticleMetadataModel).where(ArticleMetadataModel.id == article_id)
    )
    article = result.scalar_one_or_none()

    if article is None:
        raise HTTPException(status_code=404, detail="Article not found")

    await db.delete(article)
    await db.commit()

    return {"message": "Article deleted successfully"}