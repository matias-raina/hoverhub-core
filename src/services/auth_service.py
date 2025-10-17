class AuthService:
    def __init__(self, user_repository, jwt_handler):
        self.user_repository = user_repository
        self.jwt_handler = jwt_handler

    def create_token(self, user_id):
        """Generates a JWT token for the given user ID."""
        return self.jwt_handler.encode_jwt({"user_id": user_id})

    def verify_token(self, token):
        """Verifies the provided JWT token and returns the payload if valid."""
        return self.jwt_handler.decode_jwt(token)

    def authenticate_user(self, username, password):
        """Authenticates a user by checking credentials."""
        user = self.user_repository.get_user_by_username(username)
        if user and self.verify_password(password, user.password):
            return user
        return None

    def verify_password(self, plain_password, hashed_password):
        """Verifies a plain password against a hashed password."""
        return hashed_password == plain_password  # Replace with a proper hash comparison in production

    def register_user(self, username, email, password):
        """Registers a new user and returns the created user."""
        hashed_password = self.hash_password(password)
        return self.user_repository.create_user(username, email, hashed_password)

    def hash_password(self, password):
        """Hashes the password for storage."""
        return password  # Replace with a proper hashing function in production