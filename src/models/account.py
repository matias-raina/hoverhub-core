from sqlalchemy import Column, BigInteger, SmallInteger, ForeignKey, DateTime, UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from src.config.database import Base


class Account(Base):
    __tablename__ = 'accounts'
    __table_args__ = (
        UniqueConstraint('user_id', 'account_type_id',
                         name='uq_user_account_type'),
    )

    id = Column(BigInteger, primary_key=True, index=True)
    user_id = Column(BigInteger, ForeignKey(
        'users.id', ondelete='CASCADE'), nullable=False)
    account_type_id = Column(SmallInteger, ForeignKey(
        'account_types.id'), nullable=False)
    account_status_type_id = Column(SmallInteger, ForeignKey(
        'account_status_types.id'), nullable=False)
    created_at = Column(DateTime(timezone=True),
                        server_default=func.now(), nullable=False)

    # Relationships
    user = relationship("User", back_populates="accounts")
    account_type = relationship("AccountType", back_populates="accounts")
    account_status_type = relationship(
        "AccountStatusType", back_populates="accounts")
    droner_profile = relationship(
        "DronerProfile", back_populates="account", uselist=False, cascade="all, delete-orphan")
    job_poster_profile = relationship(
        "JobPosterProfile", back_populates="account", uselist=False, cascade="all, delete-orphan")
    jobs = relationship("Job", back_populates="account",
                        cascade="all, delete-orphan")
    applications = relationship(
        "Application", back_populates="account", cascade="all, delete-orphan")
    favorites = relationship(
        "Favorite", back_populates="account", cascade="all, delete-orphan")
    triggered_notifications = relationship(
        "Notification", back_populates="actor_account", foreign_keys="Notification.actor_account_id")
    job_alert_subscriptions = relationship(
        "JobAlertSubscription", back_populates="droner_account", foreign_keys="JobAlertSubscription.droner_account_id")
    targeted_alerts = relationship("JobAlertSubscription", back_populates="job_poster_account",
                                   foreign_keys="JobAlertSubscription.job_poster_account_id")

    def __repr__(self):
        return f"<Account(id={self.id}, user_id={self.user_id}, type={self.account_type_id})>"
