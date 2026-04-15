from sqlalchemy import Column, String
from sqlalchemy.orm import relationship
from core.database import Base
from sqlalchemy.dialects.postgresql import UUID
import uuid

class User(Base):
    __tablename__ = "users"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String, unique=True, index=True, nullable=False)
    name = Column(String, nullable=False)
    role = Column(String, default="user")
    google_id = Column(String, unique=True, index=True, nullable=True)
    photo = Column(String, nullable=True)

    progress = relationship("UserProgress", back_populates="user")
    threat_logs = relationship("ThreatLog", back_populates="user")