class UserService:
    def __init__(self, user_repository):
        self.user_repository = user_repository

    def get_user_by_id(self, user_id: int):
        return self.user_repository.get_user_by_id(user_id)

    def create_user(self, user_data):
        # Here you would typically hash the password and validate the data
        user_data['password'] = self.hash_password(user_data['password'])
        return self.user_repository.create_user(user_data)

    def update_user(self, user_id: int, user_data):
        # Validate and update user data
        return self.user_repository.update_user(user_id, user_data)

    def delete_user(self, user_id: int):
        return self.user_repository.delete_user(user_id)

    def hash_password(self, password: str) -> str:
        # Implement password hashing logic here
        pass

    def validate_user_data(self, user_data):
        # Implement user data validation logic here
        pass