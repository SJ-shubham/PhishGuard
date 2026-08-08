from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr, Field
from bson import ObjectId


# ── Helpers ───────────────────────────────────────────────────────────────────

class PyObjectId(str):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v, _info=None):
        if not ObjectId.is_valid(str(v)):
            raise ValueError("Invalid ObjectId")
        return str(v)


# ── DB Document ───────────────────────────────────────────────────────────────

class UserInDB(BaseModel):
    id:            Optional[PyObjectId] = Field(None, alias="_id")
    name:          str
    email:         str
    password_hash: str
    created_at:    datetime             = Field(default_factory=datetime.utcnow)
    scan_count:    int                  = 0

    class Config:
        populate_by_name = True


# ── Request schemas ───────────────────────────────────────────────────────────

class RegisterRequest(BaseModel):
    name:     str       = Field(..., min_length=2, max_length=64)
    email:    EmailStr
    password: str       = Field(..., min_length=8, max_length=128)


class LoginRequest(BaseModel):
    email:    EmailStr
    password: str


class ChangePasswordRequest(BaseModel):
    old_password: str
    new_password: str = Field(..., min_length=8, max_length=128)


# ── Response schemas ──────────────────────────────────────────────────────────

class UserResponse(BaseModel):
    id:         str
    name:       str
    email:      str
    created_at: datetime
    scan_count: int


class TokenResponse(BaseModel):
    access_token:  str
    refresh_token: str
    token_type:    str = "bearer"
