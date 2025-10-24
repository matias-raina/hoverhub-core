from sqlalchemy import Column, SmallInteger, String
from sqlalchemy.orm import relationship
from src.config.database import Base


class JobRequirementType(Base):
    __tablename__ = 'job_requirement_types'

    id = Column(SmallInteger, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False)
    description = Column(String)

    # Relationships
    job_requirements = relationship(
        "JobRequirement", back_populates="job_requirement_type")

    def __repr__(self):
        return f"<JobRequirementType(id={self.id}, name={self.name})>"
