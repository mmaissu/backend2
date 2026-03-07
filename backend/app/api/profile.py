"""Profile API — user info, stats, my publications."""
from fastapi import APIRouter, Depends
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import get_current_user
from app.infrastructure.database import get_db
from app.infrastructure.models import ArticleMetadataModel, UserModel
from app.schemas.article import ArticleMetadataResponse
from app.schemas.auth import UserResponse

router = APIRouter()


@router.get("")
async def get_profile(
    current_user: UserModel = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Profile: user info, articles count, recent publications."""
    count_result = await db.execute(
        select(func.count()).select_from(ArticleMetadataModel).where(
            ArticleMetadataModel.created_by_id == str(current_user.id)
        )
    )
    articles_count = count_result.scalar() or 0

    articles_result = await db.execute(
        select(ArticleMetadataModel)
        .where(ArticleMetadataModel.created_by_id == str(current_user.id))
        .order_by(ArticleMetadataModel.created_at.desc())
        .limit(10)
    )
    recent_articles = articles_result.scalars().all()

    return {
        "user": UserResponse.from_user(current_user),
        "articles_count": articles_count,
        "recent_articles": [ArticleMetadataResponse.model_validate(a) for a in recent_articles],
    }
