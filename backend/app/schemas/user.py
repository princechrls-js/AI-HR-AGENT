from typing import Optional, List
from pydantic import BaseModel, EmailStr, Field, field_validator
from datetime import datetime
from app.models.user import UserRole

class UserBase(BaseModel):
    name: str
    email: EmailStr
    role: UserRole
    title: Optional[str] = None
    company_name: Optional[str] = None
    bio: Optional[str] = None
    avatar_url: Optional[str] = None
    bg_url: Optional[str] = None
    resume_url: Optional[str] = None
    career: Optional[str] = None
    skills: Optional[str] = None
    company_details: Optional[str] = None
    achievements: Optional[str] = None
    employee_count: Optional[str] = None

    @field_validator("role", mode="before")
    @classmethod
    def lowercase_role(cls, v):
        if isinstance(v, str):
            return v.lower()
        return v

class UserCreate(UserBase):
    password: str

    @field_validator("password")
    @classmethod
    def password_length(cls, v: str):
        if len(v) < 6:
            raise ValueError("Password must be at least 6 characters")
        return v

class UserResponse(UserBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: Optional[str] = None

class UserUpdate(BaseModel):
    name: Optional[str] = None
    title: Optional[str] = None
    company_name: Optional[str] = None
    bio: Optional[str] = None
    avatar_url: Optional[str] = None
    bg_url: Optional[str] = None
    resume_url: Optional[str] = None
    career: Optional[str] = None
    skills: Optional[str] = None
    company_details: Optional[str] = None
    achievements: Optional[str] = None
    employee_count: Optional[str] = None
