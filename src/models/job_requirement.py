from sqlalchemy import Column, BigInteger, SmallInteger, ForeignKey, String, UniqueConstraint
from sqlalchemy.orm import relationship
from src.config.database import Base


class JobRequirement(Base):
    __tablename__ = 'job_requirements'
    __table_args__ = (
        UniqueConstraint('job_id', 'job_requirement_type_id',
                         'value', name='uq_job_requirement'),
    )

    id = Column(BigInteger, primary_key=True, index=True)
    job_id = Column(BigInteger, ForeignKey(
        'jobs.id', ondelete='CASCADE'), nullable=False)
    job_requirement_type_id = Column(SmallInteger, ForeignKey(
        'job_requirement_types.id'), nullable=False)
    value = Column(String, nullable=False)

    # Relationships
    job = relationship("Job", back_populates="job_requirements")
    job_requirement_type = relationship(
        "JobRequirementType", back_populates="job_requirements")

    def __repr__(self):
        return f"<JobRequirement(id={self.id}, job_id={self.job_id}, type={self.job_requirement_type_id}, value={self.value})>"
