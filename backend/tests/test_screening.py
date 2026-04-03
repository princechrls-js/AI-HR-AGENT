import pytest
from app.services.resume_parser_service import resume_parser_service
from app.services.scoring_service import scoring_service
import os

def test_scoring_logic():
    # Test deterministic scoring
    # Mock data
    resume_skills = ["Python", "FastAPI"]
    job_skills = "Python, FastAPI, SQL"
    resume_exp = [{"role": "Dev"}]
    job_exp_req = "2 years"
    
    # Simple check - this would normally require mock vectors too
    # but we can test the numeric parts if we mock the semantic score
    pass

def test_parser_exists():
    assert resume_parser_service is not None
