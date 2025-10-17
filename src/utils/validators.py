def validate_email(email: str) -> bool:
    import re
    email_regex = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
    return re.match(email_regex, email) is not None

def validate_password(password: str) -> bool:
    if len(password) < 8:
        return False
    if not any(char.isdigit() for char in password):
        return False
    if not any(char.isalpha() for char in password):
        return False
    return True

def validate_username(username: str) -> bool:
    return len(username) >= 3 and len(username) <= 30

def validate_job_title(title: str) -> bool:
    return len(title) > 0 and len(title) <= 100

def validate_job_description(description: str) -> bool:
    return len(description) > 0 and len(description) <= 1000

def validate_application_status(status: str) -> bool:
    valid_statuses = ['pending', 'accepted', 'rejected']
    return status in valid_statuses

def validate_favorite_job(job_id: int) -> bool:
    return job_id > 0