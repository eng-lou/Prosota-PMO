from __future__ import annotations

from dataclasses import dataclass

import jwt
from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jwt import PyJWKClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.database import get_db

_jwks_client: PyJWKClient | None = None


def _get_jwks_client() -> PyJWKClient:
    global _jwks_client
    if _jwks_client is None:
        _jwks_client = PyJWKClient(
            f"https://{settings.auth0_domain}/.well-known/jwks.json",
            cache_keys=True,
        )
    return _jwks_client


def _decode_token(token: str) -> dict:
    client = _get_jwks_client()
    signing_key = client.get_signing_key_from_jwt(token)
    return jwt.decode(
        token,
        signing_key.key,
        algorithms=["RS256"],
        audience=settings.auth0_audience,
        issuer=f"https://{settings.auth0_domain}/",
    )


@dataclass
class TokenPayload:
    sub: str
    email: str | None = None


_bearer = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(_bearer),
) -> TokenPayload:
    try:
        payload = _decode_token(credentials.credentials)
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Invalid token")
    return TokenPayload(sub=payload["sub"], email=payload.get("email"))


async def get_db_user(
    token: TokenPayload = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Return the DB User for the authenticated token, auto-provisioning on first login."""
    from app.models.organisation import Organisation
    from app.models.user import User

    result = await db.execute(select(User).where(User.auth0_sub == token.sub))
    user = result.scalar_one_or_none()
    if user:
        return user

    # First login — provision org (if none exists) and user
    org_result = await db.execute(select(Organisation).limit(1))
    org = org_result.scalar_one_or_none()
    if org is None:
        org = Organisation(name="Prosota Consulting Ltd", plan_tier="starter")
        db.add(org)
        await db.flush()

    email = token.email or f"user+{token.sub.split('|')[-1]}@prosotapmo.local"
    user = User(
        org_id=org.id,
        email=email,
        auth0_sub=token.sub,
        display_name=email,
        role="admin",
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user
