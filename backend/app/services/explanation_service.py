from app.core.config import settings
import json
import os
import requests

class ExplanationService:
    def __init__(self):
        prompt_path = os.path.join("app", "ai", "prompts", "explanation_prompt.txt")
        if os.path.exists(prompt_path):
            with open(prompt_path, "r") as f:
                self.system_prompt = f.read()
        else:
            self.system_prompt = "You are an expert HR assistant. Explain why a candidate was given a specific score for a job based on their resume."

    def _call_llm(self, system_prompt: str, user_prompt: str) -> str:
        url = "https://openrouter.ai/api/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {settings.OPENROUTER_API_KEY}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": "openrouter/auto",
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ]
        }
        response = requests.post(url, headers=headers, data=json.dumps(payload))
        if response.status_code == 200:
            return response.json()['choices'][0]['message']['content']
        raise Exception(f"LLM API error: {response.text}")

    def generate_explanation(self, job_dict: dict, resume_dict: dict, scores: dict) -> dict:
        user_prompt = f"""
        Job Description: {job_dict['job_description']}
        Required Skills: {job_dict['skills_required']}
        
        Candidate Structured Data: {json.dumps(resume_dict)}
        AI Scores: {json.dumps(scores)}
        
        Generate a human-readable explanation in JSON format with:
        - summary: A brief summary of the candidate's profile.
        - strengths: A list of candidate's strengths relative to the job.
        - missing_skills: A list of key skills or requirements missing.
        - recommendation: A clear recommendation (Hire, Interview, Reject, Hold).
        - explanation_text: A detailed paragraph explaining the reasoning.
        """
        
        try:
            response_text = self._call_llm(self.system_prompt, user_prompt)
            if "```json" in response_text:
                response_text = response_text.split("```json")[1].split("```")[0].strip()
            elif "```" in response_text:
                response_text = response_text.split("```")[1].split("```")[0].strip()
            
            return json.loads(response_text)
        except Exception:
            return {
                "summary": "AI generated result.",
                "strengths": [],
                "missing_skills": [],
                "recommendation": "Hold",
                "explanation_text": "Failed to generate detailed explanation."
            }

explanation_service = ExplanationService()
