from sqlalchemy.orm import Session
from repositories.character_repository import get_all_characters, get_character_by_id
from repositories.progress_repository import get_progress
import uuid

def get_character_status_for_user(db: Session, user_id: uuid.UUID, char, user_points: int) -> str:
    # اتحقق لو مكتمل
    progress = get_progress(db, user_id, char.id)
    if progress and progress.completed:
        return "completed"

    # لو نقاطه كافية → active
    if user_points >= char.points_required:
        return "active"

    return "locked"

def get_characters_for_user(db: Session, user_id: uuid.UUID, user_points: int):
    characters = get_all_characters(db)
    result = []

    for char in characters:
        status = get_character_status_for_user(db, user_id, char, user_points)
        result.append({
            "id": str(char.id),
            "persona": char.persona,
            "persona_desc": char.persona_desc,
            "avatar": char.avatar,
            "status": status
        })

    return result

def get_character_detail(db: Session, user_id: uuid.UUID, character_id: uuid.UUID, user_points: int):
    char = get_character_by_id(db, character_id)
    if not char:
        return None

    status = get_character_status_for_user(db, user_id, char, user_points)
    progress = get_progress(db, user_id, char.id)

    return {
        "id": str(char.id),
        "title": char.title,
        "level": char.level,
        "persona": char.persona,
        "persona_desc": char.persona_desc,
        "avatar": char.avatar,
        "target": char.target,
        "success_msg": char.success_msg,
        "points_required": char.points_required,
        "secret_category": char.secret_category,
        "status": status,
        "completed_at": str(progress.completed_at) if progress and progress.completed else None
    }