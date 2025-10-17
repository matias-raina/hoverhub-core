from sqlalchemy import Column, Integer, ForeignKey
from sqlalchemy.orm import relationship
from src.config.database import Base

class Favorite(Base):
    __tablename__ = 'favorites'

    id = Column(Integer, primary_key=True, index=True)
    job_id = Column(Integer, ForeignKey('jobs.id'), nullable=False)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)

    job = relationship("Job", back_populates="favorites")
    user = relationship("User", back_populates="favorites")