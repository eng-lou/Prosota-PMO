from __future__ import annotations

from fastapi import APIRouter, Depends

from app.core.auth import get_db_user
from app.schemas.user import UserResponse

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/me", response_model=UserResponse)
async def get_me(user=Depends(get_db_user)):
    return user
