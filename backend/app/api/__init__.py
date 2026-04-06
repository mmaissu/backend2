from fastapi import APIRouter

from app.api import admin, auth, articles, harvest, profile

router = APIRouter()

router.include_router(auth.router, prefix="/auth", tags=["auth"])
router.include_router(profile.router, prefix="/profile", tags=["profile"])
router.include_router(articles.router, prefix="/articles", tags=["articles"])
router.include_router(harvest.router)
router.include_router(admin.router)

@router.get("")
def api_root():
    return {
        "message": "Scientific Data Harvester API",
        "docs": "/api/docs",
        "redoc": "/api/redoc",
        "auth": "/api/auth",
        "articles": "/api/articles",
        "harvest": "/api/harvest",
    }
