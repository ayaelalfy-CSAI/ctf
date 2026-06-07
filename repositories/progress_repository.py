import uuid
from datetime import datetime, timezone
from sqlalchemy.orm import Session
from models.character import Character
from models.user_progress import UserProgress
from models.user import User


class ProgressRepository:

    def __init__(self, db: Session):
        self.db = db

    # ------------------------------------------------------------------
    # Core queries
    # ------------------------------------------------------------------

    def get_progress(self, user_id: uuid.UUID, character_id: uuid.UUID) -> UserProgress | None:
        return (
            self.db.query(UserProgress)
            .filter_by(user_id=user_id, character_id=character_id)
            .first()
        )

    def get_all_progress(self, user_id: uuid.UUID) -> list[UserProgress]:
        return self.db.query(UserProgress).filter_by(user_id=user_id).all()

    # ------------------------------------------------------------------
    # Status logic
    # المنطق:
    #   - completed → اليوزر خلّص الشخصية دي
    #   - active    → Level 1 دايماً، أو الشخصية اللي قبلها completed
    #   - locked    → غير كده
    # ------------------------------------------------------------------

    def get_character_status(self, user_id: uuid.UUID, character: Character) -> str:
        # 1. هل الشخصية دي مكتملة؟
        progress = self.get_progress(user_id, character.id)
        if progress and progress.completed:
            return "completed"

        # 2. Level 1 دايماً active
        if character.level == 1:
            return "active"

        # 3. جيب الشخصية اللي قبلها
        prev_character = (
            self.db.query(Character)
            .filter(Character.level == character.level - 1)  # filter() بدل filter_by() عشان أوضح
            .first()
        )

        # لو مفيش شخصية قبلها (edge case) → active
        if not prev_character:
            return "active"

        # 4. هل الشخصية اللي قبلها مكتملة؟
        prev_progress = self.get_progress(user_id, prev_character.id)
        if prev_progress and prev_progress.completed:
            return "active"

        # غير كده → locked
        return "locked"

    def is_character_unlocked(self, user_id: uuid.UUID, character_id: uuid.UUID) -> bool:
        character = self.db.query(Character).filter(Character.id == character_id).first()
        if not character:
            return False
        status = self.get_character_status(user_id, character)
        return status in ["active", "completed"]

    # ------------------------------------------------------------------
    # Complete character & award points
    # ------------------------------------------------------------------

    def complete_character(self, user_id: uuid.UUID, character_id: uuid.UUID) -> dict:
        character = self.db.query(Character).filter(Character.id == character_id).first()
        if not character:
            return {"message": "Character not found", "points_added": 0, "total_points": 0}

        # لو مكتملة أصلاً — ارجع بدون تغيير
        progress = self.get_progress(user_id, character_id)
        if progress and progress.completed:
            return {"message": "already completed", "points_added": 0}

        # عمل record لو مش موجود
        if not progress:
            progress = UserProgress(user_id=user_id, character_id=character_id)
            self.db.add(progress)

        progress.completed = True
        progress.completed_at = datetime.now(timezone.utc)

        # زوّد نقاط اليوزر بـ points_reward مش points_required
        user = self.db.query(User).filter(User.id == user_id).first()
        user.points += character.points_reward

        self.db.commit()
        self.db.refresh(user)

        return {
            "message": character.success_msg or "تم بنجاح!",
            "points_added": character.points_reward,
            "total_points": user.points,
        }