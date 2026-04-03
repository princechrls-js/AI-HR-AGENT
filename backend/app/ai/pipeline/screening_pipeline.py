from app.services.resume_parser_service import resume_parser_service
from app.services.resume_structuring_service import resume_structuring_service
from app.services.embedding_service import embedding_service
from app.services.scoring_service import scoring_service
from app.services.explanation_service import explanation_service
from app.models.job import Job
from app.models.application import Application
from app.models.parsed_resume import ParsedResume
from app.models.screening_result import ScreeningResult
from sqlalchemy.orm import Session
import json

class ScreeningPipeline:
    def run(self, db: Session, application: Application, job: Job):
        import requests
        import os
        from app.core.logging import logger

        try:
            # 1. Download resume from URL to local temp path
            temp_dir = "temp_resumes"
            os.makedirs(temp_dir, exist_ok=True)
            
            file_extension = os.path.splitext(application.resume_path.split("?")[0])[-1]
            temp_file_path = os.path.join(temp_dir, f"resume_{application.id}{file_extension}")
            
            try:
                logger.info(f"Downloading resume from {application.resume_path} to {temp_file_path}")
                response = requests.get(application.resume_path)
                if response.status_code == 200:
                    with open(temp_file_path, "wb") as f:
                        f.write(response.content)
                else:
                    logger.error(f"Failed to download resume: Status {response.status_code}")
                    temp_file_path = application.resume_path
            except Exception as e:
                logger.error(f"Error downloading resume: {str(e)}")
                temp_file_path = application.resume_path

            # 2. Extract raw text from local file
            try:
                raw_text = resume_parser_service.extract_text(temp_file_path)
                application.resume_text = raw_text
            finally:
                if os.path.exists(temp_file_path) and temp_file_path.startswith(temp_dir):
                    os.remove(temp_file_path)
            
            # 3. Structure resume
            structured_data = resume_structuring_service.structure_resume(raw_text)
            
            # Save parsed resume
            parsed_resume = ParsedResume(
                application_id=application.id,
                full_name=structured_data.get("full_name"),
                email=structured_data.get("email"),
                phone=structured_data.get("phone"),
                skills_json=structured_data.get("skills", []),
                experience_json=structured_data.get("experience", []),
                education_json=structured_data.get("education", []),
                projects_json=structured_data.get("projects", []),
                raw_text=raw_text
            )
            db.add(parsed_resume)
            
            # 3. Generate embeddings
            resume_vector = embedding_service.generate_embedding(raw_text)
            job_vector = embedding_service.generate_embedding(job.job_description)
            
            from app.services.matching_service import matching_service
            
            # 4. Calculate scores
            semantic_score = matching_service.calculate_semantic_similarity(raw_text, job.job_description)
            skill_score = matching_service.match_skills(structured_data.get("skills", []), job.skills_required)
            
            experience_score = min(len(structured_data.get("experience", [])) / 3, 1.0)
            
            final_score = (semantic_score * 0.5) + (skill_score * 0.3) + (experience_score * 0.2)
            
            scores = {
                "semantic_score": round(semantic_score, 2),
                "skill_score": round(skill_score, 2),
                "experience_score": round(experience_score, 2),
                "final_score": round(final_score, 2)
            }
            
            # 5. Generate AI Explanation
            job_dict = {
                "job_description": job.job_description,
                "skills_required": job.skills_required
            }
            explanation_data = explanation_service.generate_explanation(job_dict, structured_data, scores)
            
            # 6. Store Screening Results
            screening_result = ScreeningResult(
                application_id=application.id,
                semantic_score=scores["semantic_score"],
                skill_score=scores["skill_score"],
                experience_score=scores["experience_score"],
                final_score=scores["final_score"],
                summary=explanation_data.get("summary", ""),
                strengths_json=explanation_data.get("strengths", []),
                missing_skills_json=explanation_data.get("missing_skills", []),
                recommendation=explanation_data.get("recommendation", "Hold"),
                explanation_text=explanation_data.get("explanation_text", "")
            )
            db.add(screening_result)
            
            application.application_status = "screened"
            db.commit()
            return screening_result
        except Exception as e:
            logger.error(f"PIPELINE CRASHED: {str(e)}")
            import traceback
            logger.error(traceback.format_exc())
            db.rollback()
            raise e

screening_pipeline = ScreeningPipeline()
