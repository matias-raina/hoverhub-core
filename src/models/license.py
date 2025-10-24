from sqlalchemy import Column, BigInteger, SmallInteger, ForeignKey, Date, UniqueConstraint
from sqlalchemy.orm import relationship
from src.config.database import Base


class License(Base):
    __tablename__ = 'licenses'
    __table_args__ = (
        UniqueConstraint('droner_profile_id', 'license_type_id',
                         'expiration_date', name='uq_profile_license_type'),
    )

    id = Column(BigInteger, primary_key=True, index=True)
    droner_profile_id = Column(BigInteger, ForeignKey(
        'droner_profiles.id', ondelete='CASCADE'), nullable=False)
    license_type_id = Column(SmallInteger, ForeignKey(
        'license_types.id'), nullable=False)
    expiration_date = Column(Date)
    issued_at = Column(Date)

    # Relationships
    droner_profile = relationship("DronerProfile", back_populates="licenses")
    license_type = relationship("LicenseType", back_populates="licenses")

    def __repr__(self):
        return f"<License(id={self.id}, droner_profile_id={self.droner_profile_id}, type={self.license_type_id})>"
