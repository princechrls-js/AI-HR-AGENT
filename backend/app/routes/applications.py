from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, BackgroundTasks
from sqlalchemy.orm import Session
from app.core.database import get_db, SessionLocal
from app.models.application import Application
from app.models.job import Job
from app.models.user import User
from app.schemas.application import ApplicationResponse
from app.dependencies.roles import candidate_required
from app.dependencies.auth import get_current_user
from app.services.file_storage_service import file_storage_service
from app.services.application_service import application_service
from app.ai.pipeline.screening_pipeline import screening_pipeline
from app.core.logging import logger
from app.utils.constants import constants
from app.routes.ws import manager
from app.dependencies.roles import hr_required
from app.dependencies.auth import get_current_user
from app.core.database import get_db
from app.models.user import User
from app.models.application import Application
from app.models.job import Job
from sqlalchemy.orm import Session
from pydantic import BaseModel
import uuid
import os
from typing import List

class StatusUpdate(BaseModel):
    status: str

router = APIRouter(prefix="/applications", tags=["Applications"])

def run_screening_task(application_id: int, job_id: int):
    db = SessionLocal()
    try:
        application = db.query(Application).filter(Application.id == application_id).first()
        job = db.query(Job).filter(Job.id == job_id).first()
        if application and job:
            logger.info(f"Starting background screening for application {application_id}")
            screening_pipeline.run(db, application, job)
            logger.info(f"Completed background screening for application {application_id}")
    except Exception as e:
        import traceback
        error_msg = traceback.format_exc()
        logger.error(f"Background screening failed for application {application_id}: {error_msg}")
        with open("error_log.txt", "a") as f:
            f.write(f"\n--- Application {application_id} Error ---\n{error_msg}")
    finally:
        db.close()

@router.post("/apply", response_model=ApplicationResponse)
async def apply_to_job(
    job_id: int, 
    background_tasks: BackgroundTasks,
    resume: UploadFile = File(None), 
    db: Session = Depends(get_db), 
    current_user: User = Depends(candidate_required)
):
    # Check if job exists
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    # Check if already applied
    existing_app = db.query(Application).filter(
        Application.candidate_id == current_user.id,
        Application.job_id == job_id
    ).first()
    if existing_app:
        raise HTTPException(status_code=400, detail="Already applied to this job")

    try:
        if resume:
            # Validate file type
            extension = os.path.splitext(resume.filename)[1].lower()
            if extension not in constants.ALLOWED_EXTENSIONS:
                raise HTTPException(status_code=400, detail=f"Allowed extensions: {constants.ALLOWED_EXTENSIONS}")
            
            # Save resume
            filename = f"{uuid.uuid4()}_{resume.filename}"
            file_path = await file_storage_service.save_resume(resume, filename)
        else:
            # User wants to use their Master Profile Resume
            if not current_user.resume_url:
                raise HTTPException(status_code=400, detail="No resume uploaded. Please provide a file or upload a Master Resume to your profile.")
            file_path = current_user.resume_url
        
        # Create application via service
        new_application = await application_service.create_application(db, job_id, current_user.id, file_path)
        
        # Add background task for screening
        background_tasks.add_task(run_screening_task, new_application.id, job_id)
        
        # Create a notification for the HR user
        from app.models.notification import Notification
        hr_notification = Notification(
            user_id=job.hr_id,
            title="New Application Received",
            message=f"{current_user.name} applied for your {job.title} listing."
        )
        db.add(hr_notification)
        db.commit()

        # Emit WebSocket event to HR
        await manager.send_personal_message(
            message={
                "type": "NEW_APPLICATION",
                "job_title": job.title,
                "candidate_name": current_user.name
            },
            user_id=job.hr_id
        )

        return new_application
    except Exception as e:
        logger.error(f"Application submission failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/my", response_model=List[ApplicationResponse])
def get_my_applications(db: Session = Depends(get_db), current_user: User = Depends(candidate_required)):
    return application_service.get_candidate_applications(db, current_user.id)

@router.get("/{application_id}", response_model=ApplicationResponse)
def get_application_status(
    application_id: int, 
    db: Session = Depends(get_db), 
    current_user: User = Depends(get_current_user)
):
    application = application_service.get_application_by_id(db, application_id)
    if not application:
        raise HTTPException(status_code=404, detail="Application not found")
    
    # Ensure user is either the candidate or an HR
    if current_user.role != "hr" and application.candidate_id != current_user.id:
        raise HTTPException(status_code=403, detail="Forbidden")
        
    return application

@router.put("/{application_id}/status")
async def update_application_status(
    application_id: int, 
    status_update: StatusUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(hr_required)
):
    application = db.query(Application).filter(Application.id == application_id).first()
    if not application:
        raise HTTPException(status_code=404, detail="Application not found")
    
    # Check if HR owns the job
    job = db.query(Job).filter(Job.id == application.job_id).first()
    if not job or job.hr_id != current_user.id:
        raise HTTPException(status_code=403, detail="Forbidden")

    if status_update.status not in ["pending", "processing", "screened", "rejected", "accepted"]:
        raise HTTPException(status_code=400, detail="Invalid status")

    application.application_status = status_update.status
    db.commit()
    db.refresh(application)

    # Trigger WebSocket notification to candidate
    await manager.send_personal_message(
        message={
            "type": "APPLICATION_STATUS_UPDATE",
            "application_id": application.id,
            "job_title": job.title,
            "company_name": job.company_name,
            "status": status_update.status
        },
        user_id=application.candidate_id
    )

    # If accepted, auto-create a chat message so conversation thread exists
    if status_update.status == "accepted":
        from app.models.message import DirectMessage
        welcome_msg = DirectMessage(
            sender_id=current_user.id,
            receiver_id=application.candidate_id,
            content=f"Congratulations! Your application for \"{job.title}\" at {job.company_name} has been accepted. We'd like to schedule an interview with you. Please let us know your availability."
        )
        db.add(welcome_msg)
        db.commit()

        await manager.send_personal_message(
            message={
                "type": "CHAT_MESSAGE",
                "message_id": welcome_msg.id,
                "sender_id": current_user.id,
                "sender_name": current_user.name,
                "content": welcome_msg.content,
                "created_at": str(welcome_msg.created_at)
            },
            user_id=application.candidate_id
        )

    return {"message": "Status updated successfully", "status": application.application_status}
