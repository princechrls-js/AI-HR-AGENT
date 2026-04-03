from sqlalchemy.orm import Session
from app.models.job import Job
from app.schemas.job import JobCreate, JobUpdate
from app.services.embedding_service import embedding_service
from app.services.faiss_service import faiss_service

class JobService:
    def create_job(self, db: Session, job_in: JobCreate, hr_id: int):
        new_job = Job(**job_in.model_dump(), hr_id=hr_id)
        db.add(new_job)
        db.commit()
        db.refresh(new_job)
        
        # Generate embedding and add to FAISS
        job_text = f"{new_job.title} {new_job.job_description}"
        vector = embedding_service.generate_embedding(job_text)
        faiss_service.add_job_vector(vector, new_job.id)
        
        return new_job

    def get_job_by_id(self, db: Session, job_id: int):
        return db.query(Job).filter(Job.id == job_id).first()

    def get_hr_jobs(self, db: Session, hr_id: int):
        return db.query(Job).filter(Job.hr_id == hr_id).all()

    def update_job(self, db: Session, job: Job, job_in: JobUpdate):
        for field, value in job_in.model_dump(exclude_unset=True).items():
            setattr(job, field, value)
        db.commit()
        db.refresh(job)
        return job

    def delete_job(self, db: Session, job: Job):
        db.delete(job)
        db.commit()

job_service = JobService()
