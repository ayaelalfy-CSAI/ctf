import uuid
from sqlalchemy import Column, String, Integer, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from core.database import Base


class Character(Base):
    __tablename__ = "characters"

    id               = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title            = Column(String, nullable=False)
    level            = Column(Integer, default=1)
    persona          = Column(String, nullable=False)
    persona_desc     = Column(String)
    target           = Column(String, nullable=False)
    secret_category  = Column(String, nullable=False)
    success_msg      = Column(String)
    prompt_template  = Column(Text, nullable=False)
    points_required  = Column(Integer, default=0)
    points_reward    = Column(Integer, default=10)
    avatar           = Column(String, nullable=True)


    progress = relationship(
        "UserProgress",
        back_populates="character",
        cascade="all, delete-orphan",
    )
    threat_logs = relationship(
        "ThreatLog",
        back_populates="character",
        cascade="all, delete-orphan",
    )