import re

class SkillExtractor:
    def __init__(self, skill_database: list[str] = None):
        self.skill_database = skill_database or ["python", "java", "fastapi", "sql", "react", "docker"]

    def extract_from_text(self, text: str) -> list[str]:
        # Simple rule-based extraction
        found_skills = []
        text_lower = text.lower()
        for skill in self.skill_database:
            if re.search(rf'\b{skill}\b', text_lower):
                found_skills.append(skill)
        return found_skills

skill_extractor = SkillExtractor()
