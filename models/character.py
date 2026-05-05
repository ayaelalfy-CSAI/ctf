from sqlalchemy import Column, Integer, String, Text
from sqlalchemy.orm import relationship
from core.database import Base
from sqlalchemy.dialects.postgresql import UUID
import uuid

class Character(Base):
    __tablename__ = "characters"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title = Column(String, nullable=False)
    level = Column(Integer, default=1) 
    persona = Column(String, nullable=False)
    persona_desc = Column(String)
    target = Column(String, nullable=False)  # اللي المفروض اليوزر يطلعه
    secret_category = Column(String, nullable=False)  # ← اسم الـ category زي "apartment_numbers"
    success_msg = Column(String)
    prompt_template = Column(Text, nullable=False) # instructions to sent to the model
    points_required = Column(Integer, default=0)   # عدد النقاط اللي اليوزر محتاجه عشان يفتح الشخصية دي
    points_reward = Column(Integer, default=10)   # عدد النقاط اللي اليوزر بياخدها لما يكمل الشخصية دي
    avatar = Column(String, nullable=True)