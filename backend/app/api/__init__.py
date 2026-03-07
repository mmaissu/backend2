"""API routes."""
from fastapi import APIRouter

from app.api import auth, articles, profile

router = APIRouter()
router.include_router(auth.router, prefix="/auth", tags=["auth"])
router.include_router(profile.router, prefix="/profile", tags=["profile"])
router.include_router(articles.router, prefix="/articles", tags=["articles"])


@router.get("")
def api_root():
    """API info and links."""
    return {
        "message": "Scientific Data Harvester API",
        "docs": "/api/docs",
        "redoc": "/api/redoc",
        "auth": "/api/auth",
        "articles": "/api/articles",
    }
