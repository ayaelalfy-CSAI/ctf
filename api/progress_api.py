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

    # زود النقاط
    current_user.points += character.points_reward
    db.commit()

    return {
        "message": character.success_msg or "تم بنجاح!",
        "points_added": character.points_reward,
        "total_points": current_user.points
    }

@router.get("/characters")
def get_characters(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    characters = db.query(Character).order_by(Character.order_index).all()
    result = []
    for char in characters:
        # الشخصية الأولى مفتوحة دايماً
        if char.order_index == 1:
            is_unlocked = True
        else:
            # اتحقق إن الشخصية اللي قبلها اتخلصت
            prev = db.query(Character).filter_by(
                order_index=char.order_index - 1
            ).first()
            if prev:
                prev_progress = db.query(UserProgress).filter_by(
                    user_id=current_user.id,
                    character_id=prev.id,
                    completed=True
                ).first()
                is_unlocked = prev_progress is not None
            else:
                is_unlocked = True

        progress = db.query(UserProgress).filter_by(
            user_id=current_user.id,
            character_id=char.id
        ).first()

        result.append({
            "id": str(char.id),
            "title": char.title,
            "strength": char.strength,
            "persona": char.persona,
            "persona_desc": char.persona_desc,
            "target": char.target,
            "category": char.category,
            "success_msg": char.success_msg,
            "order_index": char.order_index,
            "points_reward": char.points_reward,
            "is_unlocked": is_unlocked,
            "is_completed": progress.completed if progress else False
        })
    return result

@router.get("/my-points")
def get_my_points(current_user: User = Depends(get_current_user)):
    return {
        "points": current_user.points,
        "name": current_user.name,
        "photo": current_user.photo
    }
    return {
        "points": current_user.points,
        "name": current_user.name,
    }