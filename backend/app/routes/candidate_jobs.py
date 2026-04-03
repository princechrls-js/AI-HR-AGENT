from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.job import Job
from app.schemas.job import JobResponse
from typing import List
from app.dependencies.auth import get_current_user_optional
import re

router = APIRouter(prefix="/jobs", tags=["Candidate Jobs"])

def calculate_heuristic_match(resume_text: str, skills_required: str) -> int:
    if not resume_text or not skills_required:
        return 0
    # Create simple word bags
    resume_words = set(re.findall(r'\b\w+\b', resume_text.lower()))
    skills_words = set(re.findall(r'\b\w+\b', skills_required.lower()))
    
    if not skills_words:
        return 0
        
    overlap = resume_words.intersection(skills_words)
    percentage = int((len(overlap) / len(skills_words)) * 100)
    
    # Boost the score naturally because resumes often use variants (simple heuristic)
    # We want it to feel realistic. A 50% strict word match usually implies a very high conceptual match.
    boosted = min(99, percentage + 35) # e.g. 50% -> 85%
    return boosted

@router.get("", response_model=List[JobResponse])
def list_jobs(db: Session = Depends(get_db), current_user = Depends(get_current_user_optional)):
    jobs = db.query(Job).all()
    
    # Calculate native match percentage if resume exists
    if current_user and getattr(current_user, 'parsed_resume_text', None):
        resume_text = current_user.parsed_resume_text
        for job in jobs:
            job.match_percentage = calculate_heuristic_match(resume_text, job.skills_required)
    
    return jobs

@router.get("/{job_id}", response_model=JobResponse)
def get_job_detail(job_id: int, db: Session = Depends(get_db), current_user = Depends(get_current_user_optional)):
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
        
    if current_user and getattr(current_user, 'parsed_resume_text', None):
        job.match_percentage = calculate_heuristic_match(current_user.parsed_resume_text, job.skills_required)
        
    return job
