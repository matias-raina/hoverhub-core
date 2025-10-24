from sqlalchemy import Column, BigInteger, ForeignKey, String, DateTime, UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from src.config.database import Base


class Application(Base):
    __tablename__ = 'applications'
    __table_args__ = (
        UniqueConstraint('job_id', 'account_id', name='uq_application'),
    )

    id = Column(BigInteger, primary_key=True, index=True)
    job_id = Column(BigInteger, ForeignKey(
        'jobs.id', ondelete='CASCADE'), nullable=False)
    account_id = Column(BigInteger, ForeignKey(
        'accounts.id', ondelete='CASCADE'), nullable=False)
    status = Column(String, nullable=False)
    message = Column(String)
    submitted_at = Column(DateTime(timezone=True),
                          server_default=func.now(), nullable=False)

    # Relationships
    job = relationship("Job", back_populates="applications")
    account = relationship("Account", back_populates="applications")
    notifications = relationship("Notification", back_populates="application")

    def __repr__(self):
        return f"<Application(id={self.id}, job_id={self.job_id}, account_id={self.account_id}, status={self.status})>"
