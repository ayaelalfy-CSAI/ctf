from sqlalchemy import Column, Integer, String, Text
from sqlalchemy.orm import relationship
from core.database import Base
from sqlalchemy.dialects.postgresql import UUID
import uuid

class Character(Base):
    __tablename__ = "characters"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title = Column(String, nullable=False)
    strength = Column(String, default="EASY")  # EASY, MEDIUM, HARD
    persona = Column(String, nullable=False)
    persona_desc = Column(String)
    target = Column(String, nullable=False)  # اللي المفروض اليوزر يطلعه
    category = Column(String)
    secret = Column(String, nullable=False)  # السر الحقيقي
    success_msg = Column(String)
    prompt_template = Column(Text, nullable=False)
    order_index = Column(Integer, default=1)
    points_reward = Column(Integer, default=10)