from sqlalchemy import Column, SmallInteger, String
from sqlalchemy.orm import relationship
from src.config.database import Base


class NotificationType(Base):
    __tablename__ = 'notification_types'

    id = Column(SmallInteger, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False)
    channel = Column(String, nullable=False)

    # Relationships
    notifications = relationship(
        "Notification", back_populates="notification_type")

    def __repr__(self):
        return f"<NotificationType(id={self.id}, name={self.name}, channel={self.channel})>"
