from datetime import datetime

from fastapi import APIRouter, Depends, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.infrastructure.database import get_db
from app.infrastructure.models import ArticleMetadataModel
from app.schemas.harvest import (
    HarvestResponse,
    ImportArticleRequest,
    ImportArticleResponse,
)
from app.services.harvest_service import (
    get_openalex_work_by_id,
    restore_abstract,
    search_openalex,
)

router = APIRouter(
    prefix="/harvest",
    tags=["Harvest"],
)


@router.get("", response_model=HarvestResponse)
async def harvest_articles(
    query: str = Query(..., min_length=2),
    years: int = Query(2, ge=1, le=10),
):
    results = await search_openalex(query=query, years=years)

    return HarvestResponse(
        query=query,
        count=len(results),
        results=results,
    )


@router.post("/import", response_model=ImportArticleResponse)
async def import_article(
    payload: ImportArticleRequest,
    db: AsyncSession = Depends(get_db),
):
    openalex_data = await get_openalex_work_by_id(payload.openalex_id)

    openalex_id = openalex_data.get("id")
    title = openalex_data.get("title") or "No title"
    doi = openalex_data.get("doi")
    cited_by_count = openalex_data.get("cited_by_count", 0)

    existing = await db.execute(
        select(ArticleMetadataModel).where(
            ArticleMetadataModel.openalex_id == openalex_id
        )
    )
    existing_article = existing.scalar_one_or_none()

    if existing_article:
        return ImportArticleResponse(
            message="Article already imported",
            article_id=existing_article.id,
        )

    authors = []
    for authorship in openalex_data.get("authorships", []):
        author = authorship.get("author", {})
        name = author.get("display_name")
        if name:
            authors.append(name)

    source = None
    primary_location = openalex_data.get("primary_location")
    if primary_location and primary_location.get("source"):
        source = primary_location["source"].get("display_name")

    published_at = None
    publication_date = openalex_data.get("publication_date")
    if publication_date:
        try:
            published_at = datetime.fromisoformat(publication_date)
        except ValueError:
            published_at = None

    abstract = restore_abstract(openalex_data.get("abstract_inverted_index"))

    article = ArticleMetadataModel(
        openalex_id=openalex_id,
        title=title,
        abstract=abstract,
        authors=authors,
        doi=doi,
        source=source,
        published_at=published_at,
        cited_by_count=cited_by_count,
        raw_metadata=openalex_data,
        keywords=None,
        created_by_id=None,
    )

    db.add(article)
    await db.commit()
    await db.refresh(article)

    return ImportArticleResponse(
        message="Article imported successfully",
        article_id=article.id,
    )