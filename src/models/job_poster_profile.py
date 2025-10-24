from sqlalchemy import Column, BigInteger, ForeignKey, String
from sqlalchemy.orm import relationship
from src.config.database import Base


class JobPosterProfile(Base):
    __tablename__ = 'job_poster_profiles'

    id = Column(BigInteger, primary_key=True, index=True)
    account_id = Column(BigInteger, ForeignKey(
        'accounts.id', ondelete='CASCADE'), unique=True, nullable=False)
    company = Column(String)
    contact_name = Column(String)
    contact_email = Column(String)

    # Relationships
    account = relationship("Account", back_populates="job_poster_profile")

    def __repr__(self):
        return f"<JobPosterProfile(id={self.id}, company={self.company})>"
