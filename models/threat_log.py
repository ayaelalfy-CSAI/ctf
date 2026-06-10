import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Integer, Boolean, DateTime, Text, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSON
from sqlalchemy.orm import relationship
from core.database import Base


class ThreatLog(Base):
    __tablename__ = "threat_logs"

    id            = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id       = Column(UUID(as_uuid=True), ForeignKey("users.id",      ondelete="CASCADE"), nullable=False)
    character_id  = Column(UUID(as_uuid=True), ForeignKey("characters.id", ondelete="CASCADE"), nullable=False)
    raw_input     = Column(Text)
    model_output  = Column(Text)
    decision      = Column(String)
    score         = Column(Integer)
    is_compromised= Column(Boolean, default=False)
    created_at    = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    trace         = Column(JSON)

    user      = relationship("User",      back_populates="threat_logs")
    character = relationship("Character", back_populates="threat_logs")  # ← أضفنا back_populates