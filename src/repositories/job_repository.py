class JobRepository:
    def __init__(self, db_session):
        self.db_session = db_session

    def get_job_by_id(self, job_id: int):
        return self.db_session.query(Job).filter(Job.id == job_id).first()

    def create_job(self, job_data: JobCreate):
        new_job = Job(**job_data.dict())
        self.db_session.add(new_job)
        self.db_session.commit()
        self.db_session.refresh(new_job)
        return new_job

    def update_job(self, job_id: int, job_data: JobCreate):
        job = self.get_job_by_id(job_id)
        if job:
            for key, value in job_data.dict().items():
                setattr(job, key, value)
            self.db_session.commit()
            return job
        return None

    def delete_job(self, job_id: int):
        job = self.get_job_by_id(job_id)
        if job:
            self.db_session.delete(job)
            self.db_session.commit()
            return True
        return False

    def get_all_jobs(self):
        return self.db_session.query(Job).all()