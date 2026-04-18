from sqlalchemy import Column, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy import UniqueConstraint
from core.database import Base
import uuid

class UserProgress(Base):
    __tablename__ = "user_progress"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    character_id = Column(UUID(as_uuid=True), ForeignKey("characters.id"), nullable=False)
    completed = Column(Boolean, default=False)
    completed_at = Column(DateTime)

    user = relationship("User", back_populates="progress")

    __table_args__ = (
        UniqueConstraint("user_id", "character_id", name="uq_user_character"),
    )