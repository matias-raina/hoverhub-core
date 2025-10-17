from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from src.schemas.job import JobCreate, JobResponse
from src.services.job_service import JobService
from src.config.database import get_db

class JobRouter:
    def __init__(self):
        self.router = APIRouter()
        self.job_service = JobService()

        self.router.add_api_route("/jobs", self.create_job, methods=["POST"], response_model=JobResponse)
        self.router.add_api_route("/jobs/{job_id}", self.get_job, methods=["GET"], response_model=JobResponse)
        self.router.add_api_route("/jobs/{job_id}", self.update_job, methods=["PUT"], response_model=JobResponse)
        self.router.add_api_route("/jobs/{job_id}", self.delete_job, methods=["DELETE"])

    async def create_job(self, job: JobCreate, db: Session = Depends(get_db)):
        return await self.job_service.create_job(job, db)

    async def get_job(self, job_id: int, db: Session = Depends(get_db)):
        job = await self.job_service.get_job_by_id(job_id, db)
        if not job:
            raise HTTPException(status_code=404, detail="Job not found")
        return job

    async def update_job(self, job_id: int, job: JobCreate, db: Session = Depends(get_db)):
        updated_job = await self.job_service.update_job(job_id, job, db)
        if not updated_job:
            raise HTTPException(status_code=404, detail="Job not found")
        return updated_job

    async def delete_job(self, job_id: int, db: Session = Depends(get_db)):
        success = await self.job_service.delete_job(job_id, db)
        if not success:
            raise HTTPException(status_code=404, detail="Job not found")
        return {"detail": "Job deleted successfully"}

job_router = JobRouter().router