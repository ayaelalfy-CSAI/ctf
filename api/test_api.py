import uuid
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from core.database import get_db
from core.deps import get_current_user
from models.user import User
from repositories.progress_repository import ProgressRepository
from repositories.character_repository import CharacterRepository

router = APIRouter(prefix="/test", tags=["Test"])


@router.post("/complete/{character_id}")
def test_complete_character(
    character_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
   
    character_repo = CharacterRepository(db)
    progress_repo = ProgressRepository(db)

    # 1. تأكد إن الشخصية موجودة
    character = character_repo.get_by_id(character_id)
    if not character:
        raise HTTPException(status_code=404, detail="Character not found")

    # 2. اعمل complete
    result = progress_repo.complete_character(current_user.id, character_id)

    # 3. جيب status الشخصية الحالية بعد الـ complete
    current_status = progress_repo.get_character_status(current_user.id, character)

    # 4. جيب الشخصية الجاية وستاتسها
    next_character = character_repo.get_by_level(character.level + 1)
    next_status = None
    if next_character:
        next_status = progress_repo.get_character_status(current_user.id, next_character)

    # 5. جيب نقاط اليوزر الحالية من الـ DB (مش من الـ cache)
    db.refresh(current_user)

    return {
        "complete_result": result,
        "current_character": {
            "id": str(character.id),
            "title": character.title,
            "level": character.level,
            "status": current_status,        # المفروض "completed"
        },
        "next_character": {
            "id": str(next_character.id) if next_character else None,
            "title": next_character.title if next_character else None,
            "level": next_character.level if next_character else None,
            "status": next_status,           # المفروض "active"
        } if next_character else None,
        "user_points": current_user.points,  # المفروض زاد بـ points_reward
    }


@router.get("/status/{character_id}")
def test_character_status(
    character_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
   
    character_repo = CharacterRepository(db)
    progress_repo = ProgressRepository(db)

    character = character_repo.get_by_id(character_id)
    if not character:
        raise HTTPException(status_code=404, detail="Character not found")

    status = progress_repo.get_character_status(current_user.id, character)

    return {
        "character_id": str(character.id),
        "title": character.title,
        "level": character.level,
        "status": status,
        "user_points": current_user.points,
    }


@router.get("/all-status")
def test_all_characters_status(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
   
    character_repo = CharacterRepository(db)
    progress_repo = ProgressRepository(db)

    characters = character_repo.get_all_ordered()

    return {
        "user_points": current_user.points,
        "characters": [
            {
                "id": str(c.id),
                "title": c.title,
                "level": c.level,
                "points_reward": c.points_reward,
                "status": progress_repo.get_character_status(current_user.id, c),
            }
            for c in characters
        ],
    }