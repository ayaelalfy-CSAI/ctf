import uuid
from sqlalchemy.orm import Session
from models.character import Character
from schemas.character_schema import CharacterCreate
 
 
class CharacterRepository:
 
    def __init__(self, db: Session):
        self.db = db
 
    def create(self, data: CharacterCreate) -> Character:
        character = Character(**data.model_dump())
        self.db.add(character)
        self.db.commit()
        self.db.refresh(character)
        return character
 
    def get_all_ordered(self) -> list[Character]:
        return self.db.query(Character).order_by(Character.level.asc()).all()
 
    def get_by_id(self, character_id: uuid.UUID) -> Character | None:
        return self.db.query(Character).filter(Character.id == character_id).first()
 
    def get_by_level(self, level: int) -> Character | None:
        return self.db.query(Character).filter(Character.level == level).first()
 
    def update(self, character: Character, data: CharacterCreate) -> Character:
        for key, value in data.model_dump(exclude_unset=True).items():
            setattr(character, key, value)
        self.db.commit()
        self.db.refresh(character)
        return character
 
    def delete(self, character: Character) -> None:
        self.db.delete(character)
        self.db.commit()
 
