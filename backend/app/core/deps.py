"""FastAPI dependencies — auth, DB, current user."""
from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import decode_access_token
from app.domain.enums import UserRole
from app.infrastructure.database import get_db
from app.infrastructure.models import UserModel

security = HTTPBearer(auto_error=False)


async def get_current_user_optional(
    db: Annotated[AsyncSession, Depends(get_db)],
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(security)],
) -> UserModel | None:
    if not credentials:
        return None
    payload = decode_access_token(credentials.credentials)
    if not payload or "sub" not in payload:
        return None
    result = await db.execute(
        select(UserModel).where(
            and_(UserModel.id == payload["sub"], UserModel.is_active == True)
        )
    )
    user = result.scalar_one_or_none()
    return user


async def get_current_user(
    user: Annotated[UserModel | None, Depends(get_current_user_optional)],
) -> UserModel:
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user


def require_role(role: UserRole):
    async def _require_role(
        current_user: Annotated[UserModel, Depends(get_current_user)],
    ) -> UserModel:
        if current_user.role != role and current_user.role != UserRole.ADMIN:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient permissions")
        return current_user

    return _require_role
