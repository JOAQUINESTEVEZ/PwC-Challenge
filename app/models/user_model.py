from sqlalchemy import Column, String, UUID, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import TIMESTAMP
from datetime import datetime
from ..db import Base
import uuid

class User(Base):
    __tablename__ = "users"
    
    id = Column(UUID, primary_key=True, default=uuid.uuid4)
    username = Column(String(50), unique=True, nullable=False)
    email = Column(String(255), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    role_id = Column(UUID, ForeignKey("roles.id"))
    client_id = Column(UUID, ForeignKey("clients.id", ondelete="CASCADE"), nullable=True)
    created_at = Column(TIMESTAMP, default=datetime.utcnow)
    updated_at = Column(TIMESTAMP, default=datetime.utcnow, onupdate=datetime.utcnow)

    role = relationship('Role', back_populates='users')
    client = relationship('Client', back_populates='users', single_parent=True)