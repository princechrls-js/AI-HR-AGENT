import re

class TextCleaner:
    @staticmethod
    def clean_text(text: str) -> str:
        # Remove extra whitespaces
        text = re.sub(r'\s+', ' ', text).strip()
        # Remove non-printable characters
        text = "".join(filter(lambda x: x.isprintable(), text))
        return text

    @staticmethod
    def extract_emails(text: str) -> list[str]:
        return re.findall(r'[\w\.-]+@[\w\.-]+', text)

    @staticmethod
    def extract_phone_numbers(text: str) -> list[str]:
        # Simple regex for phone numbers
        return re.findall(r'\+?\d[\d\s-]{8,}\d', text)

text_cleaner = TextCleaner()
