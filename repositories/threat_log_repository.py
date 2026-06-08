import uuid
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from models.threat_log import ThreatLog


class ThreatLogRepository:

    def __init__(self, db: Session):
        self.db = db

    # ------------------------------------------------------------------
    # Write
    # ------------------------------------------------------------------

    def create_log(self, data: dict) -> ThreatLog:
        log = ThreatLog(**data)
        self.db.add(log)
        self.db.commit()
        self.db.refresh(log)
        return log

    # ------------------------------------------------------------------
    # Basic reads
    # ------------------------------------------------------------------

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

    # ------------------------------------------------------------------
    # Admin dashboard queries
    # ------------------------------------------------------------------

    def get_all_logs(self, limit: int = 100, offset: int = 0) -> list[ThreatLog]:
        """All logs, newest first — paginated."""
        return (
            self.db.query(ThreatLog)
            .order_by(desc(ThreatLog.created_at))
            .offset(offset)
            .limit(limit)
            .all()
        )

    def get_logs_by_decision(self, decision: str) -> list[ThreatLog]:
        """Filter by decision: 'safe' | 'compromised' | 'blocked'."""
        return (
            self.db.query(ThreatLog)
            .filter(ThreatLog.decision == decision)
            .order_by(desc(ThreatLog.created_at))
            .all()
        )

    def get_compromised_logs(self) -> list[ThreatLog]:
        return self.get_logs_by_decision("compromised")

    def get_blocked_logs(self) -> list[ThreatLog]:
        return self.get_logs_by_decision("blocked")

    def get_stats(self) -> dict:
        """Aggregate stats for the admin dashboard overview."""
        total        = self.db.query(func.count(ThreatLog.id)).scalar()
        compromised  = self.db.query(func.count(ThreatLog.id)).filter(ThreatLog.is_compromised == True).scalar()
        blocked      = self.db.query(func.count(ThreatLog.id)).filter(ThreatLog.decision == "blocked").scalar()
        safe         = self.db.query(func.count(ThreatLog.id)).filter(ThreatLog.decision == "safe").scalar()
        avg_score    = self.db.query(func.avg(ThreatLog.score)).scalar()

        return {
            "total_prompts": total,
            "compromised": compromised,
            "blocked_by_arabguard": blocked,
            "safe": safe,
            "average_score": round(float(avg_score or 0), 2),
        }

    def get_stats_per_character(self) -> list[dict]:
        """Per-character breakdown: total / compromised / blocked."""
        rows = (
            self.db.query(
                ThreatLog.character_id,
                func.count(ThreatLog.id).label("total"),
                func.sum(
                    func.cast(ThreatLog.is_compromised, db_type=None)
                ).label("compromised"),
                func.sum(
                    func.case((ThreatLog.decision == "blocked", 1), else_=0)
                ).label("blocked"),
            )
            .group_by(ThreatLog.character_id)
            .all()
        )
        return [
            {
                "character_id": str(r.character_id),
                "total": r.total,
                "compromised": int(r.compromised or 0),
                "blocked": int(r.blocked or 0),
            }
            for r in rows
        ]

    def get_stats_per_user(self) -> list[dict]:
        """Per-user breakdown."""
        rows = (
            self.db.query(
                ThreatLog.user_id,
                func.count(ThreatLog.id).label("total"),
                func.sum(
                    func.case((ThreatLog.is_compromised == True, 1), else_=0)
                ).label("compromised"),
                func.sum(
                    func.case((ThreatLog.decision == "blocked", 1), else_=0)
                ).label("blocked"),
            )
            .group_by(ThreatLog.user_id)
            .all()
        )
        return [
            {
                "user_id": str(r.user_id),
                "total": r.total,
                "compromised": int(r.compromised or 0),
                "blocked": int(r.blocked or 0),
            }
            for r in rows
        ]

    def get_recent_attacks(self, limit: int = 20) -> list[ThreatLog]:
        """Most recent blocked or compromised prompts."""
        return (
            self.db.query(ThreatLog)
            .filter(ThreatLog.decision.in_(["blocked", "compromised"]))
            .order_by(desc(ThreatLog.created_at))
            .limit(limit)
            .all()
        )
