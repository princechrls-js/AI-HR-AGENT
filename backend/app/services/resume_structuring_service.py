from app.core.config import settings
from app.utils.text_cleaner import text_cleaner
import json
import os
import requests

class ResumeStructuringService:
    def __init__(self):
        # Load prompt from file
        prompt_path = os.path.join("app", "ai", "prompts", "resume_parser_prompt.txt")
        if os.path.exists(prompt_path):
            with open(prompt_path, "r") as f:
                self.system_prompt = f.read()
        else:
            self.system_prompt = "You are an expert HR assistant. Extract structured information from the provided resume text into JSON format."

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

    def structure_resume(self, raw_text: str) -> dict:
        user_prompt = f"Resume Text:\n{raw_text}\n\nExtract: full_name, email, phone, skills (list), experience (list of dicts), education (list of dicts), projects (list of dicts). Return ONLY valid JSON."
        
        try:
            response_text = self._call_llm(self.system_prompt, user_prompt)
            
            # Find the JSON block
            if "```json" in response_text:
                response_text = response_text.split("```json")[1].split("```")[0].strip()
            elif "```" in response_text:
                response_text = response_text.split("```")[1].split("```")[0].strip()
            
            structured_data = json.loads(response_text)
            
            # Fallbacks
            if not structured_data.get("email"):
                emails = text_cleaner.extract_emails(raw_text)
                structured_data["email"] = emails[0] if emails else ""
            
            if not structured_data.get("phone"):
                phones = text_cleaner.extract_phone_numbers(raw_text)
                structured_data["phone"] = phones[0] if phones else ""
                
            return structured_data
        except Exception:
            return {
                "full_name": "",
                "email": text_cleaner.extract_emails(raw_text)[0] if text_cleaner.extract_emails(raw_text) else "",
                "phone": text_cleaner.extract_phone_numbers(raw_text)[0] if text_cleaner.extract_phone_numbers(raw_text) else "",
                "skills": [],
                "experience": [],
                "education": [],
                "projects": []
            }

resume_structuring_service = ResumeStructuringService()
