from sqlalchemy.orm import Session
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

def get_all_progress(db: Session, user_id: uuid.UUID):
    return db.query(UserProgress).filter_by(user_id=user_id).all()

def complete_character(db: Session, user_id: uuid.UUID, character_id: uuid.UUID):
    character = db.query(Character).filter_by(id=character_id).first()
    if not character:
        return None

    progress = get_progress(db, user_id, character_id)
    if progress and progress.completed:
        return {"message": "already completed", "points_added": 0}

    if not progress:
        progress = UserProgress(
            user_id=user_id,
            character_id=character_id,
        )
        db.add(progress)

    progress.completed = True
    progress.completed_at = datetime.now(timezone.utc)

    user = db.query(User).filter_by(id=user_id).first()
    user.points += character.points_reward
    db.commit()
    db.refresh(user)

    return {
        "message": character.success_msg or "تم بنجاح!",
        "points_added": character.points_reward,
        "total_points": user.points
    }

def is_character_unlocked(db: Session, user_id: uuid.UUID, character_id: uuid.UUID) -> bool:
    character = db.query(Character).filter_by(id=character_id).first()
    if not character:
        return False

    if character.order_index == 1:
        return True

    prev_character = db.query(Character).filter_by(
        order_index=character.order_index - 1
    ).first()
    if not prev_character:
        return True

    prev_progress = db.query(UserProgress).filter_by(
        user_id=user_id,
        character_id=prev_character.id,
        completed=True
    ).first()

    return prev_progress is not None
    character = db.query(Character).filter_by(id=character_id).first()
    if not character:
        return False

    # الشخصية الأولى مفتوحة دايماً
    if character.order_index == 1:
        return True

    # جيب الشخصية اللي قبلها
    prev_character = db.query(Character).filter_by(
        order_index=character.order_index - 1
    ).first()
    if not prev_character:
        return True

    # اتحقق إن اليوزر خلّص كل levels الشخصية السابقة
    total_levels = db.query(Level).filter_by(
        character_id=prev_character.id
    ).count()

    completed_levels = db.query(UserProgress).filter_by(
        user_id=user_id,
        character_id=prev_character.id,
        completed=True
    ).count()

    return completed_levels >= total_levels