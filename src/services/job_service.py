class JobService:
    def __init__(self, job_repository):
        self.job_repository = job_repository

    def get_job_by_id(self, job_id):
        return self.job_repository.get(job_id)

    def create_job(self, job_data):
        return self.job_repository.add(job_data)

    def update_job(self, job_id, job_data):
        job = self.job_repository.get(job_id)
        if job:
            for key, value in job_data.items():
                setattr(job, key, value)
            return self.job_repository.update(job)
        return None

    def delete_job(self, job_id):
        return self.job_repository.delete(job_id)

    def get_all_jobs(self):
        return self.job_repository.get_all()