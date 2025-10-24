from sqlalchemy import Column, BigInteger, SmallInteger, ForeignKey, Boolean, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from src.config.database import Base


class JobAlertSubscription(Base):
    __tablename__ = 'job_alert_subscriptions'

    id = Column(BigInteger, primary_key=True, index=True)
    droner_account_id = Column(BigInteger, ForeignKey(
        'accounts.id', ondelete='CASCADE'), nullable=False)
    job_category_id = Column(SmallInteger, ForeignKey('job_categories.id'))
    job_poster_account_id = Column(BigInteger, ForeignKey('accounts.id'))
    is_active = Column(Boolean, nullable=False, default=True)
    created_at = Column(DateTime(timezone=True),
                        server_default=func.now(), nullable=False)

    # Relationships
    droner_account = relationship(
        "Account", back_populates="job_alert_subscriptions", foreign_keys=[droner_account_id])
    job_category = relationship(
        "JobCategory", back_populates="job_alert_subscriptions")
    job_poster_account = relationship(
        "Account", back_populates="targeted_alerts", foreign_keys=[job_poster_account_id])

    def __repr__(self):
        return f"<JobAlertSubscription(id={self.id}, droner_account_id={self.droner_account_id}, active={self.is_active})>"
