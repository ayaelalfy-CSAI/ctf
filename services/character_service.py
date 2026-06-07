import uuid
from fastapi import HTTPException
from repositories.character_repository import CharacterRepository
from repositories.progress_repository import ProgressRepository
from schemas.character_schema import (
    CharacterCreate,
    CharacterAdminResponse,
    CharacterUserResponse,
)
 
 
class CharacterService:
 
    def __init__(self, character_repo: CharacterRepository, progress_repo: ProgressRepository = None):
        self.character_repo = character_repo
        self.progress_repo = progress_repo  # مش مطلوب في الـ admin endpoints
 
    # ─── Admin methods ────────────────────────────────────────────────────────
 
    def create_character(self, data: CharacterCreate) -> dict:
        character = self.character_repo.create(data)
        return {
            "message": "Character created successfully",
            "character_id": str(character.id),
        }
 
    def get_all_characters(self) -> list[CharacterAdminResponse]:
        characters = self.character_repo.get_all_ordered()
        return [CharacterAdminResponse.model_validate(c) for c in characters]
 
    def update_character(self, character_id: uuid.UUID, data: CharacterCreate) -> dict:
        character = self.character_repo.get_by_id(character_id)
        if not character:
            raise HTTPException(status_code=404, detail="Character not found")
        self.character_repo.update(character, data)
        return {"message": "Character updated successfully"}
 
    def delete_character(self, character_id: uuid.UUID) -> dict:
        character = self.character_repo.get_by_id(character_id)
        if not character:
            raise HTTPException(status_code=404, detail="Character not found")
        self.character_repo.delete(character)
        return {"message": "Character deleted successfully"}
 
    # ─── User methods ─────────────────────────────────────────────────────────
 
    def get_characters_for_user(self, user_id: uuid.UUID) -> list[CharacterUserResponse]:
        characters = self.character_repo.get_all_ordered()
        result = []
        for c in characters:
            status = self.progress_repo.get_character_status(user_id, c)
            result.append(
                CharacterUserResponse(
                    id=c.id,
                    title=c.title,
                    level=c.level,
                    persona=c.persona,
                    persona_desc=c.persona_desc,
                    target=c.target,
                    avatar=c.avatar,
                    points_required=c.points_required,
                    points_reward=c.points_reward,
                    status=status,
                )
            )
        return result
 
    def get_character_detail(
        self,
        user_id: uuid.UUID,
        character_id: uuid.UUID,
    ) -> CharacterUserResponse | None:
        character = self.character_repo.get_by_id(character_id)
        if not character:
            return None
 
        status = self.progress_repo.get_character_status(user_id, character)
 
        return CharacterUserResponse(
            id=character.id,
            title=character.title,
            level=character.level,
            persona=character.persona,
            persona_desc=character.persona_desc,
            target=character.target,
            avatar=character.avatar,
            points_required=character.points_required,
            points_reward=character.points_reward,
            status=status,
        )




