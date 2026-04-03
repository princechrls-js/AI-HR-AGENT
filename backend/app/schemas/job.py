from typing import Optional, List
from pydantic import BaseModel, field_validator
from datetime import datetime

class JobBase(BaseModel):
    title: str
    company_name: str
    location: str
    employment_type: str
    experience_required: str
    skills_required: str
    job_description: str

    @field_validator("title", "company_name", "job_description")
    @classmethod
    def not_empty(cls, v: str):
        if not v.strip():
            raise ValueError("Field cannot be empty")
        return v

class JobCreate(JobBase):
    pass

class JobUpdate(BaseModel):
    title: Optional[str] = None
    company_name: Optional[str] = None
    location: Optional[str] = None
    employment_type: Optional[str] = None
    experience_required: Optional[str] = None
    skills_required: Optional[str] = None
    job_description: Optional[str] = None

class JobResponse(JobBase):
    id: int
    hr_id: int
    match_percentage: Optional[int] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
