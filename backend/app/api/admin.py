from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import get_current_user
from app.domain.enums import UserRole
from app.infrastructure.database import get_db
from app.infrastructure.models import ArticleMetadataModel, UserModel

router = APIRouter(prefix="/admin", tags=["admin"])


def ensure_admin(user: UserModel):
    if user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required",
        )


@router.get("/users")
async def get_all_users(
    db: AsyncSession = Depends(get_db),
    current_user: UserModel = Depends(get_current_user),
):
    ensure_admin(current_user)

    result = await db.execute(select(UserModel).order_by(UserModel.created_at.desc()))
    users = result.scalars().all()

    return [
        {
            "id": user.id,
            "email": user.email,
            "full_name": user.full_name,
            "role": user.role.value if hasattr(user.role, "value") else str(user.role),
            "is_active": user.is_active,
        }
        for user in users
    ]


@router.get("/articles")
async def get_all_articles(
    db: AsyncSession = Depends(get_db),
    current_user: UserModel = Depends(get_current_user),
):
    ensure_admin(current_user)

    result = await db.execute(
        select(ArticleMetadataModel).order_by(ArticleMetadataModel.created_at.desc())
    )
    articles = result.scalars().all()

    return [
        {
            "id": article.id,
            "title": article.title,
            "authors": article.authors,
            "doi": article.doi,
            "source": article.source,
            "cited_by_count": article.cited_by_count,
        }
        for article in articles
    ]


@router.delete("/users/{user_id}")
async def delete_user(
    user_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: UserModel = Depends(get_current_user),
):
    ensure_admin(current_user)

    if current_user.id == user_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You cannot delete yourself",
        )

    result = await db.execute(select(UserModel).where(UserModel.id == user_id))
    user = result.scalar_one_or_none()

    if user is None:
        raise HTTPException(status_code=404, detail="User not found")

    await db.delete(user)
    await db.commit()

    return {"message": "User deleted successfully"}


@router.delete("/articles/{article_id}")
async def delete_article_admin(
    article_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: UserModel = Depends(get_current_user),
):
    ensure_admin(current_user)

    result = await db.execute(
        select(ArticleMetadataModel).where(ArticleMetadataModel.id == article_id)
    )
    article = result.scalar_one_or_none()

    if article is None:
        raise HTTPException(status_code=404, detail="Article not found")

    await db.delete(article)
    await db.commit()

    return {"message": "Article deleted successfully"}