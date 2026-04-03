from typing import Optional, List
from pydantic import BaseModel
from datetime import datetime

class ParsedResumeResponse(BaseModel):
    id: int
    application_id: int
    full_name: Optional[str]
    email: Optional[str]
    phone: Optional[str]
    skills_json: Optional[str]
    experience_json: Optional[str]
    education_json: Optional[str]
    projects_json: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True
