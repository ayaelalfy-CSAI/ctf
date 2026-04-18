from sqlalchemy.orm import Session
from models.threat_log import ThreatLog
import uuid

def create_log(db: Session, data: dict):
    log = ThreatLog(**data)
    db.add(log)
    db.commit()
    db.refresh(log)
    return log

def get_logs_by_session(db: Session, session_id: str):
    return db.query(ThreatLog).filter_by(session_id=session_id).all()

def get_logs_by_user(db: Session, user_id: uuid.UUID):
    return db.query(ThreatLog).filter_by(user_id=user_id).order_by(
        ThreatLog.created_at.desc()
    ).all()

def get_logs_by_character(db: Session, character_id: uuid.UUID):
    return db.query(ThreatLog).filter_by(character_id=character_id).all()