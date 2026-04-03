def validate_email(email: str) -> bool:
    import re
    return bool(re.match(r"[^@]+@[^@]+\.[^@]+", email))

def validate_phone(phone: str) -> bool:
    import re
    return bool(re.match(r"^\+?1?\d{9,15}$", phone))
