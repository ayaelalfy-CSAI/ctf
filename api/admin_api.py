from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from core.database import get_db
from core.deps import get_admin_user
from models.user import User
from models.character import Character
from schemas.character_schema import CharacterCreate
import uuid

router = APIRouter(prefix="/admin", tags=["Admin"])

@router.post("/characters")
def create_character(
    body: CharacterCreate,
    db: Session = Depends(get_db),
    admin: User = Depends(get_admin_user)
):
    existing = db.query(Character).filter_by(order_index=body.order_index).first()
    if existing:
        raise HTTPException(status_code=400, detail="order_index already exists")

    character = Character(
        id=uuid.uuid4(),
        title=body.title,
        strength=body.strength,
        persona=body.persona,
        persona_desc=body.persona_desc,
        target=body.target,
        category=body.category,
        secret=body.secret,
        success_msg=body.success_msg,
        prompt_template=body.prompt_template,
        order_index=body.order_index,
        points_reward=body.points_reward
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
    characters = db.query(Character).order_by(Character.order_index).all()
    return [
        {
            "id": str(c.id),
            "title": c.title,
            "strength": c.strength,
            "persona": c.persona,
            "target": c.target,
            "secret": c.secret,
            "order_index": c.order_index,
            "points_reward": c.points_reward
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

    for key, value in body.model_dump().items():
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