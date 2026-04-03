from app.services.embedding_service import embedding_service
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

class MatchingService:
    def calculate_semantic_similarity(self, text1: str, text2: str) -> float:
        vector1 = embedding_service.generate_embedding(text1)
        vector2 = embedding_service.generate_embedding(text2)
        return float(cosine_similarity(vector1.reshape(1, -1), vector2.reshape(1, -1))[0][0])

    def match_skills(self, resume_skills: list[str], job_skills: str) -> float:
        job_skills_list = [s.strip().lower() for s in job_skills.split(",")]
        resume_skills_lower = [s.lower() for s in resume_skills]
        
        if not job_skills_list:
            return 1.0
            
        match_count = 0
        for skill in job_skills_list:
            if any(skill in rs or rs in skill for rs in resume_skills_lower):
                match_count += 1
        
        return match_count / len(job_skills_list)

matching_service = MatchingService()
