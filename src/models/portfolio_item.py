from sqlalchemy import Column, BigInteger, ForeignKey, String, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from src.config.database import Base


class PortfolioItem(Base):
    __tablename__ = 'portfolio_items'

    id = Column(BigInteger, primary_key=True, index=True)
    droner_profile_id = Column(BigInteger, ForeignKey(
        'droner_profiles.id', ondelete='CASCADE'), nullable=False)
    title = Column(String, nullable=False)
    media_url = Column(String, nullable=False)
    description = Column(String)
    created_at = Column(DateTime(timezone=True),
                        server_default=func.now(), nullable=False)

    # Relationships
    droner_profile = relationship(
        "DronerProfile", back_populates="portfolio_items")

    def __repr__(self):
        return f"<PortfolioItem(id={self.id}, title={self.title})>"
