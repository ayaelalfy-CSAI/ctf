# repositories/user_repository.py

from sqlalchemy.orm import Session, joinedload
from models import User, UserProgress

class ProfileRepository:

    @staticmethod
    def get_user_with_progress(db: Session, user_id: str):
        return (
            db.query(User)
            .options(
                joinedload(User.progress)  
            )
            .filter(User.id == user_id)
            .first()
        )

    @staticmethod
    def get_user_rank(db: Session, user_id: str):
        users = db.query(User).order_by(User.points.desc()).all()
        rank = next((i + 1 for i, u in enumerate(users) if u.id == user_id), None)
        return rank, len(users)