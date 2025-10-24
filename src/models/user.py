from sqlalchemy import Column, Integer, String, BigInteger
from sqlalchemy.orm import relationship
from src.config.database import Base


class User(Base):
    __tablename__ = 'users'

    id = Column(BigInteger, primary_key=True, index=True)
    firstname = Column(String, nullable=False)
    lastname = Column(String, nullable=False)
    username = Column(String, unique=True, nullable=False, index=True)
    email = Column(String, unique=True, nullable=False, index=True)
    password = Column(String, nullable=False)

    # Relationships
    accounts = relationship(
        "Account", back_populates="user", cascade="all, delete-orphan")
    notifications = relationship(
        "Notification", back_populates="recipient_user", foreign_keys="Notification.recipient_user_id")

    def __repr__(self):
        return f"<User(id={self.id}, username={self.username}, email={self.email})>"
