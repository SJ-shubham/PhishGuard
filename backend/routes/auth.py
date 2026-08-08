from datetime import timezone, timedelta, datetime

from fastapi import APIRouter, Depends, HTTPException, status
from bson import ObjectId

from backend.database import get_db
from backend.middleware.auth_guard import get_current_user
from backend.models.user import (
    RegisterRequest, LoginRequest, ChangePasswordRequest,
    TokenResponse, UserResponse,
)
from backend.services.auth_service import (
    hash_password, verify_password,
    create_access_token, create_refresh_token,
    decode_token, blacklist_token, is_blacklisted,
    get_user_by_email,
)
from backend.config import get_settings
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi import Request

_settings = get_settings()
router = APIRouter()
_bearer = HTTPBearer()


# ── Register ──────────────────────────────────────────────────────────────────

@router.post("/register", response_model=TokenResponse, status_code=201)
async def register(body: RegisterRequest, db=Depends(get_db)):
    if await get_user_by_email(body.email, db):
        raise HTTPException(status_code=409, detail="Email already registered")

    doc = {
        "name":          body.name,
        "email":         body.email.lower(),
        "password_hash": hash_password(body.password),
        "created_at":    datetime.now(timezone.utc),
        "scan_count":    0,
    }
    result  = await db["users"].insert_one(doc)
    user_id = str(result.inserted_id)

    return TokenResponse(
        access_token=create_access_token(user_id),
        refresh_token=create_refresh_token(user_id),
    )


# ── Login ─────────────────────────────────────────────────────────────────────

@router.post("/login", response_model=TokenResponse)
async def login(body: LoginRequest, db=Depends(get_db)):
    user = await get_user_by_email(body.email.lower(), db)
    if not user or not verify_password(body.password, user["password_hash"]):
        raise HTTPException(status_code=401, detail="Invalid email or password")

    user_id = str(user["_id"])
    return TokenResponse(
        access_token=create_access_token(user_id),
        refresh_token=create_refresh_token(user_id),
    )


# ── Refresh ───────────────────────────────────────────────────────────────────

@router.post("/refresh", response_model=TokenResponse)
async def refresh(
    credentials: HTTPAuthorizationCredentials = Depends(_bearer),
    db = Depends(get_db),
):
    token   = credentials.credentials
    payload = decode_token(token)

    if not payload or payload.get("type") != "refresh":
        raise HTTPException(status_code=401, detail="Invalid refresh token")

    if await is_blacklisted(token):
        raise HTTPException(status_code=401, detail="Refresh token revoked")

    user_id = payload["sub"]
    # Blacklist used refresh token
    exp = payload.get("exp", 0)
    ttl = max(int(exp - datetime.now(timezone.utc).timestamp()), 1)
    await blacklist_token(token, ttl)

    return TokenResponse(
        access_token=create_access_token(user_id),
        refresh_token=create_refresh_token(user_id),
    )


# ── Logout ────────────────────────────────────────────────────────────────────

@router.post("/logout", status_code=204)
async def logout(
    credentials: HTTPAuthorizationCredentials = Depends(_bearer),
):
    token   = credentials.credentials
    payload = decode_token(token)
    if payload:
        exp = payload.get("exp", 0)
        ttl = max(int(exp - datetime.now(timezone.utc).timestamp()), 1)
        await blacklist_token(token, ttl)


# ── Me ────────────────────────────────────────────────────────────────────────

@router.get("/me", response_model=UserResponse)
async def me(current_user=Depends(get_current_user)):
    return UserResponse(
        id         = str(current_user["_id"]),
        name       = current_user["name"],
        email      = current_user["email"],
        created_at = current_user["created_at"],
        scan_count = current_user.get("scan_count", 0),
    )


# ── Change Password ───────────────────────────────────────────────────────────

@router.put("/change-password", status_code=204)
async def change_password(
    body:         ChangePasswordRequest,
    current_user: dict = Depends(get_current_user),
    db            = Depends(get_db),
):
    if not verify_password(body.old_password, current_user["password_hash"]):
        raise HTTPException(status_code=400, detail="Old password is incorrect")

    await db["users"].update_one(
        {"_id": current_user["_id"]},
        {"$set": {"password_hash": hash_password(body.new_password)}},
    )


# ── Delete Account ────────────────────────────────────────────────────────────

@router.delete("/delete-account", status_code=204)
async def delete_account(
    current_user: dict = Depends(get_current_user),
    db            = Depends(get_db),
):
    uid = current_user["_id"]
    await db["scans"].delete_many({"user_id": str(uid)})
    await db["users"].delete_one({"_id": uid})
