from sqlalchemy import Column, BigInteger, SmallInteger, ForeignKey, String, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from src.config.database import Base


class Notification(Base):
    __tablename__ = 'notifications'

    id = Column(BigInteger, primary_key=True, index=True)
    recipient_user_id = Column(BigInteger, ForeignKey(
        'users.id', ondelete='CASCADE'), nullable=False)
    actor_account_id = Column(BigInteger, ForeignKey('accounts.id'))
    notification_type_id = Column(SmallInteger, ForeignKey(
        'notification_types.id'), nullable=False)
    job_id = Column(BigInteger, ForeignKey('jobs.id', ondelete='SET NULL'))
    application_id = Column(BigInteger, ForeignKey(
        'applications.id', ondelete='SET NULL'))
    message = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True),
                        server_default=func.now(), nullable=False)
    read_at = Column(DateTime(timezone=True))

    # Relationships
    recipient_user = relationship(
        "User", back_populates="notifications", foreign_keys=[recipient_user_id])
    actor_account = relationship(
        "Account", back_populates="triggered_notifications", foreign_keys=[actor_account_id])
    notification_type = relationship(
        "NotificationType", back_populates="notifications")
    job = relationship("Job", back_populates="notifications")
    application = relationship("Application", back_populates="notifications")

    def __repr__(self):
        return f"<Notification(id={self.id}, recipient_user_id={self.recipient_user_id}, type={self.notification_type_id})>"
