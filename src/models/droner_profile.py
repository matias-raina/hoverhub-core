from sqlalchemy import Column, BigInteger, SmallInteger, ForeignKey, String
from sqlalchemy.orm import relationship
from src.config.database import Base


class DronerProfile(Base):
    __tablename__ = 'droner_profiles'

    id = Column(BigInteger, primary_key=True, index=True)
    account_id = Column(BigInteger, ForeignKey(
        'accounts.id', ondelete='CASCADE'), unique=True, nullable=False)
    display_name = Column(String, nullable=False)
    bio = Column(String)
    experience_years = Column(SmallInteger)

    # Relationships
    account = relationship("Account", back_populates="droner_profile")
    licenses = relationship(
        "License", back_populates="droner_profile", cascade="all, delete-orphan")
    portfolio_items = relationship(
        "PortfolioItem", back_populates="droner_profile", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<DronerProfile(id={self.id}, display_name={self.display_name})>"
