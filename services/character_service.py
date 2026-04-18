from sqlalchemy.orm import Session
from repositories.character_repository import (
    get_all_characters,
    get_character_by_id,
    is_character_unlocked_repo
)
from repositories.progress_repository import (
    get_progress,
    is_character_unlocked
)
import uuid

def get_characters_for_user(db: Session, user_id: uuid.UUID):
    characters = get_all_characters(db)
    result = []
    for char in characters:
        unlocked = is_character_unlocked(db, user_id, char.id)
        progress = get_progress(db, user_id, char.id)
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
            "is_unlocked": unlocked,
            "is_completed": progress.completed if progress else False
        })
    return result