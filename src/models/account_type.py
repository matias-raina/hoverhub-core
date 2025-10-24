from sqlalchemy import Column, SmallInteger, String
from sqlalchemy.orm import relationship
from src.config.database import Base


class AccountType(Base):
    __tablename__ = 'account_types'

    id = Column(SmallInteger, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False)

    # Relationships
    accounts = relationship("Account", back_populates="account_type")

    def __repr__(self):
        return f"<AccountType(id={self.id}, name={self.name})>"
