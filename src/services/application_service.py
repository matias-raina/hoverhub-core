class ApplicationService:
    def __init__(self, application_repository):
        self.application_repository = application_repository

    def submit_application(self, user_id, job_id):
        application_data = {
            "user_id": user_id,
            "job_id": job_id,
            "status": "submitted"
        }
        return self.application_repository.submit_application(application_data)

    def get_applications(self, user_id):
        return self.application_repository.get_applications_by_user(user_id)

    def update_application_status(self, application_id, status):
        return self.application_repository.update_status(application_id, status)

    def get_application_by_id(self, application_id):
        return self.application_repository.get_application_by_id(application_id)