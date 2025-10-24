from sqlalchemy import Column, BigInteger, ForeignKey, DateTime, UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from src.config.database import Base


class Favorite(Base):
    __tablename__ = 'favorites'
    __table_args__ = (
        UniqueConstraint('job_id', 'account_id', name='uq_favorite'),
    )

    id = Column(BigInteger, primary_key=True, index=True)
    job_id = Column(BigInteger, ForeignKey(
        'jobs.id', ondelete='CASCADE'), nullable=False)
    account_id = Column(BigInteger, ForeignKey(
        'accounts.id', ondelete='CASCADE'), nullable=False)
    created_at = Column(DateTime(timezone=True),
                        server_default=func.now(), nullable=False)

    # Relationships
    job = relationship("Job", back_populates="favorites")
    account = relationship("Account", back_populates="favorites")

    def __repr__(self):
        return f"<Favorite(id={self.id}, job_id={self.job_id}, account_id={self.account_id})>"
