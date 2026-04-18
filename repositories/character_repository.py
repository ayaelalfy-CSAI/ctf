from sqlalchemy.orm import Session
from models.character import Character
import uuid

def get_all_characters(db: Session):
    return db.query(Character).order_by(Character.order_index).all()

def get_character_by_id(db: Session, character_id: uuid.UUID):
    return db.query(Character).filter_by(id=character_id).first()

def get_character_by_order(db: Session, order_index: int):
    return db.query(Character).filter_by(order_index=order_index).first()

def create_character(db: Session, data: dict):
    character = Character(**data)
    db.add(character)
    db.commit()
    db.refresh(character)
    return character

def update_character(db: Session, character_id: uuid.UUID, data: dict):
    character = db.query(Character).filter_by(id=character_id).first()
    if not character:
        return None
    for key, value in data.items():
        setattr(character, key, value)
    db.commit()
    db.refresh(character)
    return character

def delete_character(db: Session, character_id: uuid.UUID):
    character = db.query(Character).filter_by(id=character_id).first()
    if not character:
        return None
    db.delete(character)
    db.commit()
    return True