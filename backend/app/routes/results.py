from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.screening_result import ScreeningResult
from app.models.application import Application
from app.schemas.screening_result import ScreeningResultResponse
from app.dependencies.auth import get_current_user
from app.models.user import User
from typing import List

router = APIRouter(prefix="/results", tags=["Screening Results"])

@router.get("/{application_id}", response_model=ScreeningResultResponse)
def get_application_result(
    application_id: int, 
    db: Session = Depends(get_db), 
    current_user: User = Depends(get_current_user)
):
    application = db.query(Application).filter(Application.id == application_id).first()
    if not application:
        raise HTTPException(status_code=404, detail="Application not found")
    
    # Check permissions
    if current_user.role != "hr" and application.candidate_id != current_user.id:
        raise HTTPException(status_code=403, detail="Forbidden")
        
    result = db.query(ScreeningResult).filter(ScreeningResult.application_id == application_id).first()
    if not result:
        raise HTTPException(status_code=404, detail="Result not found or screening in progress")
    return result

@router.get("/job/{job_id}", response_model=List[ScreeningResultResponse])
def get_job_results(
    job_id: int, 
    db: Session = Depends(get_db), 
    current_user: User = Depends(get_current_user)
):
    # Usually only HR should see all results for a job
    if current_user.role != "hr":
        raise HTTPException(status_code=403, detail="Forbidden")
        
    results = db.query(ScreeningResult).join(Application).filter(Application.job_id == job_id).all()
    return results
