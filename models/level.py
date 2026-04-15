from sqlalchemy import Column, Integer, Text, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy import UniqueConstraint
from core.database import Base
import uuid

class Level(Base):
    __tablename__ = "levels"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    character_id = Column(UUID(as_uuid=True), ForeignKey("characters.id"), nullable=False)
    level_number = Column(Integer, nullable=False)
    system_prompt = Column(Text, nullable=False)

    character = relationship("Character", back_populates="levels")

    __table_args__ = (
        UniqueConstraint("character_id", "level_number", name="uq_character_level"),
    )