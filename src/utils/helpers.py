def hash_password(password: str) -> str:
    # Function to hash a password using a secure hashing algorithm
    import bcrypt
    hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    return hashed.decode('utf-8')

def generate_random_string(length: int) -> str:
    # Function to generate a random string of fixed length
    import random
    import string
    characters = string.ascii_letters + string.digits
    return ''.join(random.choice(characters) for _ in range(length))