from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from core.database import get_db
from core.deps import get_current_user
from models.user import User
from models.character import Character
from models.user_progress import UserProgress
from repositories.progress_repository import get_character_status, complete_character
from datetime import datetime, timezone
import uuid

router = APIRouter(prefix="/progress", tags=["Progress"])

@router.post("/complete/{character_id}")
def complete_character_endpoint(
    character_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    character = db.query(Character).filter_by(id=character_id).first()
    if not character:
        raise HTTPException(status_code=404, detail="Character not found")

    status = get_character_status(db, current_user.id, character)
    if status == "locked":
        raise HTTPException(status_code=403, detail="Character is locked!")
    if status == "completed":
        return {"message": "already completed", "points_added": 0}

    result = complete_character(db, current_user.id, character_id)
    return result

@router.get("/characters")
def get_characters(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    characters = db.query(Character).order_by(Character.level).all()
    result = []

    for char in characters:
        status = get_character_status(db, current_user.id, char)
        result.append({
            "id": str(char.id),
            "persona": char.persona,
            "persona_desc": char.persona_desc,
            "avatar": char.avatar,
            "target": char.target,
            "level": char.level,
            "points_required": char.points_required,
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