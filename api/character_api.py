from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from core.database import get_db
from core.deps import get_current_user
from models.user import User
from services.character_service import get_characters_for_user, get_character_detail
import uuid

router = APIRouter(prefix="/characters", tags=["Characters"])

@router.get("/")
def get_characters(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return get_characters_for_user(db, current_user.id, current_user.points)


@router.get("/{character_id}")
def get_character(
    character_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    result = get_character_detail(
        db,
        current_user.id,
        character_id,
        current_user.points  # ← ده الناقص
    )
    if not result:
        raise HTTPException(status_code=404, detail="Character not found")
    if result["status"] == "locked":
        raise HTTPException(status_code=403, detail="Character is locked!")
    return result