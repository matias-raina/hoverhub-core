from sqlalchemy import Column, SmallInteger, String
from sqlalchemy.orm import relationship
from src.config.database import Base


class JobCategory(Base):
    __tablename__ = 'job_categories'

    id = Column(SmallInteger, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False)

    # Relationships
    job_category_assignments = relationship(
        "JobCategoryAssignment", back_populates="job_category", cascade="all, delete-orphan")
    job_alert_subscriptions = relationship(
        "JobAlertSubscription", back_populates="job_category")

    def __repr__(self):
        return f"<JobCategory(id={self.id}, name={self.name})>"
