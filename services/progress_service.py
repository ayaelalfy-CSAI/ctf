import uuid
from fastapi import HTTPException
from repositories.character_repository import CharacterRepository
from repositories.progress_repository import ProgressRepository
from schemas.progress_schema import (
    CharacterProgressResponse,
    CompleteCharacterResponse,
    MyPointsResponse,
)
from models.user import User
 
 
class ProgressService:
 
    def __init__(self, character_repo: CharacterRepository, progress_repo: ProgressRepository):
        self.character_repo = character_repo
        self.progress_repo = progress_repo
 
    def complete_character(self, user_id: uuid.UUID, character_id: uuid.UUID) -> CompleteCharacterResponse:
        # تأكد إن الشخصية موجودة
        character = self.character_repo.get_by_id(character_id)
        if not character:
            raise HTTPException(status_code=404, detail="Character not found")
 
        # تأكد من الـ status
        status = self.progress_repo.get_character_status(user_id, character)
        if status == "locked":
            raise HTTPException(status_code=403, detail="Character is locked!")
        if status == "completed":
            return CompleteCharacterResponse(message="already completed", points_added=0)
 
        result = self.progress_repo.complete_character(user_id, character_id)
        return CompleteCharacterResponse(**result)
 
    def get_characters_with_status(self, user_id: uuid.UUID) -> list[CharacterProgressResponse]:
        characters = self.character_repo.get_all_ordered()
        result = []
        for char in characters:
            status = self.progress_repo.get_character_status(user_id, char)
            result.append(
                CharacterProgressResponse(
                    id=char.id,
                    persona=char.persona,
                    persona_desc=char.persona_desc,
                    avatar=char.avatar,
                    target=char.target,
                    level=char.level,
                    points_required=char.points_required,
                    status=status,
                )
            )
        return result
 
    def get_my_points(self, current_user: User) -> MyPointsResponse:
        return MyPointsResponse(
            points=current_user.points,
            name=current_user.name,
            photo=current_user.photo,
        )
 
