import uuid
from sqlalchemy.orm import Session
from models.threat_log import ThreatLog
 
 
class ThreatLogRepository:
 
    def __init__(self, db: Session):
        self.db = db
 
    def create_log(self, data: dict) -> ThreatLog:
        log = ThreatLog(**data)
        self.db.add(log)
        self.db.commit()
        self.db.refresh(log)
        return log
 
    def get_logs_by_session(self, session_id: str) -> list[ThreatLog]:
        return self.db.query(ThreatLog).filter_by(session_id=session_id).all()
 
    def get_logs_by_user(self, user_id: uuid.UUID) -> list[ThreatLog]:
        return (
            self.db.query(ThreatLog)
            .filter_by(user_id=user_id)
            .order_by(ThreatLog.created_at.desc())
            .all()
        )
 
    def get_logs_by_character(self, character_id: uuid.UUID) -> list[ThreatLog]:
        return self.db.query(ThreatLog).filter_by(character_id=character_id).all()
