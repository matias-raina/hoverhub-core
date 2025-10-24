from sqlalchemy import Column, BigInteger, ForeignKey, String, Numeric, Date, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from src.config.database import Base


class Job(Base):
    __tablename__ = 'jobs'

    id = Column(BigInteger, primary_key=True, index=True)
    account_id = Column(BigInteger, ForeignKey(
        'accounts.id', ondelete='CASCADE'), nullable=False)
    title = Column(String, nullable=False)
    description = Column(String, nullable=False)
    budget = Column(Numeric(12, 2))
    location = Column(String)
    start_date = Column(Date)
    end_date = Column(Date)
    created_at = Column(DateTime(timezone=True),
                        server_default=func.now(), nullable=False)

    # Relationships
    account = relationship("Account", back_populates="jobs")
    job_requirements = relationship(
        "JobRequirement", back_populates="job", cascade="all, delete-orphan")
    job_category_assignments = relationship(
        "JobCategoryAssignment", back_populates="job", cascade="all, delete-orphan")
    applications = relationship(
        "Application", back_populates="job", cascade="all, delete-orphan")
    favorites = relationship(
        "Favorite", back_populates="job", cascade="all, delete-orphan")
    notifications = relationship("Notification", back_populates="job")

    def __repr__(self):
        return f"<Job(id={self.id}, title={self.title}, account_id={self.account_id})>"
