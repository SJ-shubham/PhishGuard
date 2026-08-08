from datetime import datetime, timezone, timedelta
from typing import Optional

import bcrypt
from jose import JWTError, jwt
from bson import ObjectId

from backend.config import get_settings
from backend.redis_client import get_redis

_settings = get_settings()

# ── Password ──────────────────────────────────────────────────────────────────

def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()


def verify_password(plain: str, hashed: str) -> bool:
    return bcrypt.checkpw(plain.encode(), hashed.encode())


# ── JWT ───────────────────────────────────────────────────────────────────────

def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


def create_access_token(user_id: str) -> str:
    expire  = _utcnow() + timedelta(minutes=_settings.access_token_expire_minutes)
    payload = {"sub": user_id, "type": "access", "exp": expire}
    return jwt.encode(payload, _settings.jwt_secret, algorithm=_settings.jwt_algorithm)


def create_refresh_token(user_id: str) -> str:
    expire  = _utcnow() + timedelta(days=_settings.refresh_token_expire_days)
    payload = {"sub": user_id, "type": "refresh", "exp": expire}
    return jwt.encode(payload, _settings.jwt_secret, algorithm=_settings.jwt_algorithm)


def decode_token(token: str) -> Optional[dict]:
    try:
        return jwt.decode(token, _settings.jwt_secret, algorithms=[_settings.jwt_algorithm])
    except JWTError:
        return None


# ── Blacklist (Redis — optional) ──────────────────────────────────────────────

async def blacklist_token(token: str, expires_in_seconds: int) -> None:
    try:
        await get_redis().setex(f"blacklist:{token}", expires_in_seconds, "1")
    except Exception:
        pass  # Redis down — token expires naturally via JWT exp claim


async def is_blacklisted(token: str) -> bool:
    try:
        result = await get_redis().get(f"blacklist:{token}")
        return result is not None
    except Exception:
        return False  # Fail open: Redis down → not blacklisted


# ── User helpers ──────────────────────────────────────────────────────────────

async def get_user_by_email(email: str, db):
    return await db["users"].find_one({"email": email})


async def get_user_by_id(user_id: str, db):
    try:
        return await db["users"].find_one({"_id": ObjectId(user_id)})
    except Exception:
        return None
