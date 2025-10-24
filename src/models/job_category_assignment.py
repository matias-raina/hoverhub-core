from sqlalchemy import Column, BigInteger, SmallInteger, ForeignKey
from sqlalchemy.orm import relationship
from src.config.database import Base


class JobCategoryAssignment(Base):
    __tablename__ = 'job_category_assignments'

    job_id = Column(BigInteger, ForeignKey(
        'jobs.id', ondelete='CASCADE'), primary_key=True)
    job_category_id = Column(SmallInteger, ForeignKey(
        'job_categories.id'), primary_key=True)

    # Relationships
    job = relationship("Job", back_populates="job_category_assignments")
    job_category = relationship(
        "JobCategory", back_populates="job_category_assignments")

    def __repr__(self):
        return f"<JobCategoryAssignment(job_id={self.job_id}, category_id={self.job_category_id})>"
