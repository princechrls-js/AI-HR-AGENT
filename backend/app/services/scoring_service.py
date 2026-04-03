import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

class ScoringService:
    def calculate_scores(self, resume_vector: np.ndarray, job_vector: np.ndarray, resume_skills: list[str], job_skills: str, resume_exp: list[dict], job_exp_req: str) -> dict:
        # 1. Job Description Match (Semantic Similarity) (60%)
        semantic_score = float(cosine_similarity(resume_vector.reshape(1, -1), job_vector.reshape(1, -1))[0][0])
        
        # 2. Skill Match (40%)
        job_skills_list = [s.strip().lower() for s in job_skills.split(",")] if job_skills else []
        resume_skills_lower = [s.lower() for s in resume_skills]
        
        match_count = 0
        if job_skills_list:
            for skill in job_skills_list:
                if any(skill in rs or rs in skill for rs in resume_skills_lower):
                    match_count += 1
            skill_score = match_count / len(job_skills_list)
        else:
            skill_score = 1.0 # If no skills specified, assume match
        
        # 3. Experience Relevance (Now metadata for total score, but JD and Skills drive the result)
        experience_score = min(len(resume_exp) / 3, 1.0)
        
        # Final weighted score focusing on JD and Skills as requested
        final_score = (semantic_score * 0.6) + (skill_score * 0.4)
        
        return {
            "semantic_score": round(semantic_score, 2),
            "skill_score": round(skill_score, 2),
            "experience_score": round(experience_score, 2),
            "final_score": round(final_score, 2)
        }

scoring_service = ScoringService()
