# this file defines all the models realated to managing custom data schemas
from sqlalchemy import Column, String, Integer, ForeignKey, DateTime, Boolean
from .base import Base
from sqlalchemy.orm import relationship
from dependencies.enums import RoleEnum
from sqlalchemy import Enum as SQLAlchemyEnum
# from .organization import Organization

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    tokens = relationship("Token", back_populates="user")
    role = Column(SQLAlchemyEnum(RoleEnum), unique=False, nullable=False)
    
    # Add organization relationship
    # organization_id = Column(Integer, ForeignKey('organizations.id'), nullable=True)
    # organization = relationship("Organization", back_populates="users")
    # is_organization_owner = Column(Boolean, default=False)

    # Add the relationship to Organization
    # organizations = relationship("Organization", back_populates="owner")

# auth token
class Token(Base):
    __tablename__ = "tokens"

    id = Column(Integer, primary_key=True, index=True)
    token = Column(String, index=True)
    expires_at = Column(DateTime)
    user_id = Column(Integer, ForeignKey('users.id'))
    is_active = Column(Boolean, default=True)

    user = relationship("User", back_populates="tokens")

