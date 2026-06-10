import uuid
from sqlalchemy import Column, String, Integer
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from core.database import Base


class User(Base):
    __tablename__ = "users"

    id        = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email     = Column(String, unique=True, index=True, nullable=False)
    name      = Column(String, nullable=False)
    role      = Column(String, default="user")
    google_id = Column(String, unique=True, index=True, nullable=True)
    photo     = Column(String, nullable=True)
    points    = Column(Integer, default=0)

    # لما تحذف user بيحذف كل الـ progress والـ logs تبعه تلقائياً
    progress    = relationship("UserProgress", back_populates="user", cascade="all, delete-orphan")
    threat_logs = relationship("ThreatLog",    back_populates="user", cascade="all, delete-orphan")

    @property
    def completed_levels_count(self):
        return sum(1 for p in self.progress if p.completed)

    @property
    def completed_levels(self):
        return [p for p in self.progress if p.completed]