from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
import uuid

from core.database import get_db
from core.deps import get_admin_user
from models.user import User
from models.character import Character
from schemas.character_schema import CharacterCreate

router = APIRouter(prefix="/admin", tags=["Admin"])


@router.post("/characters")
def create_character(
    body: CharacterCreate,
    db: Session = Depends(get_db),
    admin: User = Depends(get_admin_user)
):
    character = Character(
        title=body.title,
        level=body.level,
        persona=body.persona,
        persona_desc=body.persona_desc,
        target=body.target,
        secret_category=body.secret_category,
        success_msg=body.success_msg,
        prompt_template=body.prompt_template,
        points_required=body.points_required,
        avatar=body.avatar,
    )

    db.add(character)
    db.commit()
    db.refresh(character)

    return {
        "message": "Character created successfully",
        "character_id": str(character.id)
    }


@router.get("/characters")
def get_all_characters(
    db: Session = Depends(get_db),
    admin: User = Depends(get_admin_user)
):
    characters = db.query(Character)\
                   .order_by(Character.level.asc())\
                   .all()

    return [
        {
            "id": str(c.id),
            "title": c.title,
            "level": c.level,
            "persona": c.persona,
            "persona_desc": c.persona_desc,
            "target": c.target,
            "secret_category": c.secret_category,
            "success_msg": c.success_msg,
            "prompt_template": c.prompt_template,
            "points_required": c.points_required,
            "avatar": c.avatar,
        }
        for c in characters
    ]


@router.put("/characters/{character_id}")
def update_character(
    character_id: uuid.UUID,
    body: CharacterCreate,
    db: Session = Depends(get_db),
    admin: User = Depends(get_admin_user)
):
    character = db.query(Character).filter_by(id=character_id).first()
    if not character:
        raise HTTPException(status_code=404, detail="Character not found")

    for key, value in body.model_dump(exclude_unset=True).items():
        setattr(character, key, value)

    db.commit()
    db.refresh(character)

    return {"message": "Character updated successfully"}


@router.delete("/characters/{character_id}")
def delete_character(
    character_id: uuid.UUID,
    db: Session = Depends(get_db),
    admin: User = Depends(get_admin_user)
):
    character = db.query(Character).filter_by(id=character_id).first()
    if not character:
        raise HTTPException(status_code=404, detail="Character not found")

    db.delete(character)
    db.commit()

    return {"message": "Character deleted successfully"}