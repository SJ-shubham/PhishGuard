from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from backend.services.auth_service import decode_token, is_blacklisted, get_user_by_id
from backend.database import get_db

_bearer = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(_bearer),
    db = Depends(get_db),
):
    token = credentials.credentials
    payload = decode_token(token)

    if not payload or payload.get("type") != "access":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="Invalid or expired token")

    if await is_blacklisted(token):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="Token has been revoked")

    user = await get_user_by_id(payload["sub"], db)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="User not found")

    return user
