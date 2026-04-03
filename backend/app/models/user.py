from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Enum
from sqlalchemy.orm import relationship
from app.core.database import Base
import enum

class UserRole(str, enum.Enum):
    HR = "hr"
    CANDIDATE = "candidate"

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)
    role = Column(String, nullable=False, index=True) # Store enum as string
    
    # Profile fields
    title = Column(String, nullable=True) # Headline/Role
    company_name = Column(String, nullable=True) # Only for HR
    bio = Column(String, nullable=True) # Description
    avatar_url = Column(String, nullable=True)
    bg_url = Column(String, nullable=True)
    resume_url = Column(String, nullable=True)
    parsed_resume_text = Column(String, nullable=True)
    career = Column(String, nullable=True) # Career summary/Professional journey
    skills = Column(String, nullable=True) # Skills/Focus Areas
    
    # HR Specific Fields
    company_details = Column(String, nullable=True)
    achievements = Column(String, nullable=True)
    employee_count = Column(String, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    jobs = relationship("Job", back_populates="hr")
    applications = relationship("Application", back_populates="candidate")
    posts = relationship("Post", back_populates="author")
