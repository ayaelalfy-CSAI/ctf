from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from core.database import get_db
from core.deps import get_current_user
from models.user import User
from models.character import Character
from models.user_progress import UserProgress
from datetime import datetime, timezone
import uuid

router = APIRouter(prefix="/progress", tags=["Progress"])

@router.post("/complete/{character_id}")
def complete_character(
    character_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    character = db.query(Character).filter_by(id=character_id).first()
    if not character:
        raise HTTPException(status_code=404, detail="Character not found")

    # اتحقق إن الشخصية مفتوحة
    if current_user.points < character.points_required:
        raise HTTPException(status_code=403, detail="Character is locked!")

    # اتحقق إنه مش خلّصه قبل كده
    progress = db.query(UserProgress).filter_by(
        user_id=current_user.id,
        character_id=character_id
    ).first()

    if progress and progress.completed:
        return {"message": "already completed", "points_added": 0}

    if not progress:
        progress = UserProgress(
            user_id=current_user.id,
            character_id=character_id,
        )
        db.add(progress)

    progress.completed = True
    progress.completed_at = datetime.now(timezone.utc)

    # الـ reward حسب الـ level
    POINTS_REWARD = {1: 10, 2: 20, 3: 30, 4: 40, 5: 50, 6: 60, 7: 70, 8: 80}
    points_earned = POINTS_REWARD.get(character.level, 10)
    current_user.points += points_earned
    db.commit()

    return {
        "message": character.success_msg or "تم بنجاح!",
        "points_added": points_earned,
        "total_points": current_user.points
    }

@router.get("/characters")
def get_characters(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    characters = db.query(Character).order_by(Character.level).all()
    result = []
    has_active = False  # ← علم عشان نعمل active واحد بس

    for char in characters:
        progress = db.query(UserProgress).filter_by(
            user_id=current_user.id,
            character_id=char.id
        ).first()

        if progress and progress.completed:
            status = "completed"
        elif not has_active and current_user.points >= char.points_required:
            status = "active"
            has_active = True  # ← بعد ما نعمل واحد active مش هنعمل تاني
        else:
            status = "locked"

        result.append({
            "id": str(char.id),
            "persona": char.persona,
            "persona_desc": char.persona_desc,
            "avatar": char.avatar,
            "target": char.target,
            "level": char.level,
            "status": status
        })

    return result

@router.get("/my-points")
def get_my_points(current_user: User = Depends(get_current_user)):
    return {
        "points": current_user.points,
        "name": current_user.name,
        "photo": current_user.photo
    }

