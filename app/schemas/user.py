import re
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr, Field, field_validator

from app.models.user import UserRole

class UserCreate(BaseModel):

    name: str = Field(
        ...,
        min_length=2,
        max_length=100,
        examples=["Jane Doe"],
        description="Full display name (2–100 characters).",
    )
    email: EmailStr = Field(
        ...,
        examples=["jane@example.com"],
        description="Unique email address used for login.",
    )
    password: str = Field(
        ...,
        min_length=8,
        examples=["S3cur3P@ss!"],
        description=(
            "Password (min 8 chars, must include an uppercase letter, "
            "a lowercase letter, a digit, and a special character)."
        ),
    )

    @field_validator("password")
    @classmethod
    def password_strength(cls, v: str) -> str:
        errors: list[str] = []
        if not re.search(r"[A-Z]", v):
            errors.append("at least one uppercase letter")
        if not re.search(r"[a-z]", v):
            errors.append("at least one lowercase letter")
        if not re.search(r"\d", v):
            errors.append("at least one digit")
        if not re.search(r"[^A-Za-z0-9]", v):
            errors.append("at least one special character")
        if errors:
            raise ValueError("Password must contain: " + ", ".join(errors))
        return v

    @field_validator("name")
    @classmethod
    def name_no_blank(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("Name cannot be blank or whitespace only.")
        return v.strip()

    model_config = {"str_strip_whitespace": True}

class UserLogin(BaseModel):

    email: EmailStr = Field(..., examples=["jane@example.com"])
    password: str = Field(..., min_length=1, examples=["S3cur3P@ss!"])

    model_config = {"str_strip_whitespace": True}

class UserResponse(BaseModel):

    id: int
    name: str
    email: str
    role: UserRole          # typed enum so callers can compare against UserRole.ADMIN etc.
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}

class RoleUpdate(BaseModel):

    role: UserRole = Field(
        ...,
        examples=["admin", "member"],
        description="New role to assign: 'admin' or 'member'.",
    )

class Token(BaseModel):

    access_token: str
    token_type: str = "bearer"
    user: UserResponse

class TokenData(BaseModel):

    user_id: Optional[int] = None
