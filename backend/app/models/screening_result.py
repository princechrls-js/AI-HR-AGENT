from datetime import datetime
from sqlalchemy import Column, Integer, Float, Text, DateTime, ForeignKey, String, JSON
from sqlalchemy.orm import relationship
from app.core.database import Base

class ScreeningResult(Base):
    __tablename__ = "screening_results"

    id = Column(Integer, primary_key=True, index=True)
    application_id = Column(Integer, ForeignKey("applications.id"), nullable=False)
    semantic_score = Column(Float, nullable=False)
    skill_score = Column(Float, nullable=False)
    experience_score = Column(Float, nullable=False)
    final_score = Column(Float, nullable=False)
    summary = Column(Text, nullable=False)
    strengths_json = Column(JSON, nullable=False) # JSON list
    missing_skills_json = Column(JSON, nullable=False) # JSON list
    recommendation = Column(String, nullable=False)
    explanation_text = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    application = relationship("Application", back_populates="screening_result")
