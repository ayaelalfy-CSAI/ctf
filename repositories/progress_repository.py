from sqlalchemy.orm import Session
from models.user_progress import UserProgress
from models.character import Character
from models.user import User
from datetime import datetime, timezone
import uuid


def get_progress(db: Session, user_id: uuid.UUID, character_id: uuid.UUID):
    return db.query(UserProgress).filter_by(
        user_id=user_id,
        character_id=character_id
    ).first()


def get_character_status(db: Session, user_id: uuid.UUID, character: Character) -> str:
    # اتحقق لو مكتمل
    progress = get_progress(db, user_id, character.id)
    if progress and progress.completed:
        return "completed"

    # المستوى الأول دايماً active
    if character.level == 1:
        return "active"

    # جيب الشخصية اللي في المستوى اللي قبله
    prev_character = db.query(Character).filter_by(
        level=character.level - 1
    ).first()

    if not prev_character:
        return "active"

    # اتحقق لو الشخصية اللي قبلها مكتملة
    prev_progress = get_progress(db, user_id, prev_character.id)
    if prev_progress and prev_progress.completed:
        return "active"

    return "locked"


def complete_character(db: Session, user_id: uuid.UUID, character_id: uuid.UUID):
    character = db.query(Character).filter_by(id=character_id).first()
    if not character:
        return None

    # اتحقق لو already completed
    progress = get_progress(db, user_id, character_id)
    if progress and progress.completed:
        return {"message": "already completed", "points_added": 0}

    # اعمل progress لو مش موجود
    if not progress:
        progress = UserProgress(
            user_id=user_id,
            character_id=character_id,
        )
        db.add(progress)

    # mark as completed
    progress.completed = True
    progress.completed_at = datetime.now(timezone.utc)

    # زود نقاط اليوزر
    user = db.query(User).filter_by(id=user_id).first()
    user.points += character.points_required

    db.commit()
    db.refresh(user)

    return {
        "message": character.success_msg or "تم بنجاح!",
        "points_added": character.points_required,
        "total_points": user.points
    }


def get_all_progress(db: Session, user_id: uuid.UUID):
    return db.query(UserProgress).filter_by(user_id=user_id).all()


def is_character_unlocked(db: Session, user_id: uuid.UUID, character_id: uuid.UUID) -> bool:
    character = db.query(Character).filter_by(id=character_id).first()
    if not character:
        return False

    user = db.query(User).filter_by(id=user_id).first()
    if not user:
        return False

    return user.points >= character.points_required