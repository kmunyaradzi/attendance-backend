import hashlib
from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.config import REFRESH_TOKEN_DAYS
from app.core.deps import get_current_user
from app.core.security import verify_password
from app.core.tokens import create_access_token, create_refresh_token
from app.db import get_db
from app.models import RefreshToken, User
from app.schemas.auth import (
    LoginRequest,
    LoginResponse,
    TokenPair,
    TokenRefreshRequest,
    UserRead,
)

router = APIRouter()


def _unauthorized(detail: str) -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail=detail,
    )


@router.post("/login", response_model=LoginResponse)
def login(payload: LoginRequest, db: Session = Depends(get_db)) -> LoginResponse:
    user = db.query(User).filter(User.email == payload.email).first()
    if (
        user is None
        or not user.is_active
        or not verify_password(payload.password, user.hashed_password)
    ):
        raise _unauthorized("Invalid credentials.")

    raw_token, token_hash = create_refresh_token()
    refresh_record = RefreshToken(
        user_id=user.id,
        token_hash=token_hash,
        expires_at=datetime.now(timezone.utc)
        + timedelta(days=REFRESH_TOKEN_DAYS),
    )
    db.add(refresh_record)
    db.commit()

    return LoginResponse(
        access_token=create_access_token(user.id, user.role),
        refresh_token=raw_token,
        user=UserRead.model_validate(user),
    )


@router.post("/refresh", response_model=TokenPair)
def refresh(
    payload: TokenRefreshRequest,
    db: Session = Depends(get_db),
) -> TokenPair:
    token_hash = hashlib.sha256(payload.refresh_token.encode()).hexdigest()
    stored_token = (
        db.query(RefreshToken)
        .filter(RefreshToken.token_hash == token_hash)
        .with_for_update()
        .first()
    )
    now = datetime.now(timezone.utc)
    if stored_token is None:
        raise _unauthorized("Invalid refresh token.")

    expires_at = stored_token.expires_at
    if expires_at.tzinfo is None:
        expires_at = expires_at.replace(tzinfo=timezone.utc)
    if stored_token.revoked or expires_at <= now:
        raise _unauthorized("Invalid refresh token.")

    user = db.get(User, stored_token.user_id)
    if user is None or not user.is_active:
        raise _unauthorized("Invalid refresh token.")

    stored_token.revoked = True
    new_raw_token, new_token_hash = create_refresh_token()
    db.add(
        RefreshToken(
            user_id=user.id,
            token_hash=new_token_hash,
            expires_at=now + timedelta(days=REFRESH_TOKEN_DAYS),
        )
    )
    db.commit()

    return TokenPair(
        access_token=create_access_token(user.id, user.role),
        refresh_token=new_raw_token,
    )


@router.get("/me", response_model=UserRead)
def read_current_user(
    current_user: User = Depends(get_current_user),
) -> User:
    return current_user
