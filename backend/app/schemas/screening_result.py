from typing import Optional, List
from pydantic import BaseModel
from datetime import datetime

class ScreeningResultResponse(BaseModel):
    id: int
    application_id: int
    semantic_score: float
    skill_score: float
    experience_score: float
    final_score: float
    summary: str
    strengths_json: List[str]
    missing_skills_json: List[str]
    recommendation: str
    explanation_text: str
    created_at: datetime

    class Config:
        from_attributes = True
