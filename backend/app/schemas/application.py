from typing import Optional, List
from pydantic import BaseModel
from datetime import datetime

class ApplicationBase(BaseModel):
    job_id: int

class ApplicationCreate(ApplicationBase):
    pass

class ApplicationCandidate(BaseModel):
    name: str
    title: Optional[str] = None
    avatar_url: Optional[str] = None

    class Config:
        from_attributes = True

class ApplicationResponse(ApplicationBase):
    id: int
    candidate_id: int
    resume_path: str
    application_status: str
    created_at: datetime
    updated_at: datetime
    candidate: Optional[ApplicationCandidate] = None

    class Config:
        from_attributes = True
