from sqlalchemy.orm import Session, joinedload
from app.models.application import Application
from app.services.file_storage_service import file_storage_service
import uuid

class ApplicationService:
    async def create_application(self, db: Session, job_id: int, candidate_id: int, file_path: str):
        new_application = Application(
            job_id=job_id,
            candidate_id=candidate_id,
            resume_path=file_path,
            application_status="processing"
        )
        db.add(new_application)
        db.commit()
        db.refresh(new_application)
        return new_application

    def get_candidate_applications(self, db: Session, candidate_id: int):
        return db.query(Application).options(joinedload(Application.candidate)).filter(Application.candidate_id == candidate_id).all()

    def get_application_by_id(self, db: Session, app_id: int):
        return db.query(Application).options(joinedload(Application.candidate)).filter(Application.id == app_id).first()

application_service = ApplicationService()
