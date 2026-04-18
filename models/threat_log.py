from sqlalchemy import Column, String, Integer, Boolean, DateTime, Text, JSON, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
from core.database import Base
from datetime import datetime, timezone
import uuid

class ThreatLog(Base):
    __tablename__ = "threat_logs"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    character_id = Column(UUID(as_uuid=True), ForeignKey("characters.id"), nullable=False)
    session_id = Column(String, index=True)
    raw_input = Column(Text)
    model_output = Column(Text)
    decision = Column(String)
    score = Column(Integer)
    is_compromised = Column(Boolean, default=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    trace = Column(JSON)

    user = relationship("User", back_populates="threat_logs")