from sqlalchemy import Column, SmallInteger, String
from sqlalchemy.orm import relationship
from src.config.database import Base


class LicenseType(Base):
    __tablename__ = 'license_types'

    id = Column(SmallInteger, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False)
    description = Column(String)

    # Relationships
    licenses = relationship("License", back_populates="license_type")

    def __repr__(self):
        return f"<LicenseType(id={self.id}, name={self.name})>"
