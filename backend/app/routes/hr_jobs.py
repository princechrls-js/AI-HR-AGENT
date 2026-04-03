from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.job import Job
from app.models.user import User
from app.schemas.job import JobCreate, JobResponse, JobUpdate
from app.dependencies.roles import hr_required
from app.services.job_service import job_service
from typing import List

router = APIRouter(prefix="/hr/jobs", tags=["HR Jobs"])

@router.post("", response_model=JobResponse)
def create_job(job_in: JobCreate, db: Session = Depends(get_db), current_user: User = Depends(hr_required)):
    return job_service.create_job(db, job_in, current_user.id)

@router.get("", response_model=List[JobResponse])
def get_my_jobs(db: Session = Depends(get_db), current_user: User = Depends(hr_required)):
    return job_service.get_hr_jobs(db, current_user.id)

@router.get("/{job_id}", response_model=JobResponse)
def get_job(job_id: int, db: Session = Depends(get_db), current_user: User = Depends(hr_required)):
    job = job_service.get_job_by_id(db, job_id)
    if not job or job.hr_id != current_user.id:
        raise HTTPException(status_code=404, detail="Job not found")
    return job

@router.put("/{job_id}", response_model=JobResponse)
def update_job(job_id: int, job_in: JobUpdate, db: Session = Depends(get_db), current_user: User = Depends(hr_required)):
    job = job_service.get_job_by_id(db, job_id)
    if not job or job.hr_id != current_user.id:
        raise HTTPException(status_code=404, detail="Job not found")
    return job_service.update_job(db, job, job_in)

@router.delete("/{job_id}")
def delete_job(job_id: int, db: Session = Depends(get_db), current_user: User = Depends(hr_required)):
    job = job_service.get_job_by_id(db, job_id)
    if not job or job.hr_id != current_user.id:
        raise HTTPException(status_code=404, detail="Job not found")
    job_service.delete_job(db, job)
    return {"message": "Job deleted"}
