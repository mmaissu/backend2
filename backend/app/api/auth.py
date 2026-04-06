"""Auth endpoints: register, login, logout, me."""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import get_settings
from app.core.deps import get_current_user
from app.core.security import create_access_token, get_password_hash, verify_password
from app.domain.enums import UserRole
from app.infrastructure.database import get_db
from app.infrastructure.models import UserModel
from app.schemas.auth import Token, UserCreate, UserLogin, UserResponse

router = APIRouter()


@router.post("/register", response_model=UserResponse)
async def register(
    body: UserCreate,
    db: AsyncSession = Depends(get_db),
) -> UserResponse:
    result = await db.execute(select(UserModel).where(UserModel.email == body.email))
    if result.scalar_one_or_none() is not None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )

    settings = get_settings()
    is_admin = (
        settings.initial_admin_email is not None
        and body.email.strip().lower() == settings.initial_admin_email.strip().lower()
    )

    user = UserModel(
        email=body.email,
        hashed_password=get_password_hash(body.password),
        full_name=body.full_name,
        role=UserRole.ADMIN if is_admin else UserRole.USER,
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)

    return UserResponse.from_user(user)


@router.post("/login", response_model=Token)
async def login(
    body: UserLogin,
    db: AsyncSession = Depends(get_db),
) -> Token:
    result = await db.execute(select(UserModel).where(UserModel.email == body.email))
    user = result.scalar_one_or_none()

    if not user or not verify_password(body.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User is disabled",
        )

    access_token = create_access_token(subject=str(user.id), role=user.role)
    return Token(access_token=access_token, token_type="bearer")


@router.get("/me", response_model=UserResponse)
async def me(current_user: UserModel = Depends(get_current_user)) -> UserResponse:
    return UserResponse.from_user(current_user)


@router.post("/logout")
async def logout() -> dict:
    return {"message": "Logged out. Discard the token on the client."}