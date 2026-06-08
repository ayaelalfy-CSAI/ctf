import uuid
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from core.database import get_db
from core.deps import get_current_user
from models.user import User
from repositories.character_repository import CharacterRepository
from repositories.progress_repository import ProgressRepository
from services.character_service import CharacterService
from schemas.character_schema import CharacterUserResponse
from schemas.character_schema import CharacterListItem

router = APIRouter(prefix="/characters", tags=["Characters"])


def get_character_service(db: Session = Depends(get_db)) -> CharacterService:
    return CharacterService(
        character_repo=CharacterRepository(db),
        progress_repo=ProgressRepository(db),
    )


@router.get("/", response_model=list[CharacterUserResponse])
def get_characters(
    service: CharacterService = Depends(get_character_service),
    current_user: User = Depends(get_current_user),
):
    return service.get_characters_for_user(current_user.id)


@router.get("/with_status", response_model=list[CharacterListItem])
def get_characters_summary(
    service: CharacterService = Depends(get_character_service),
    current_user: User = Depends(get_current_user),
):
    return service.get_characters_summary(current_user.id)


@router.get("/{character_id}", response_model=CharacterUserResponse)
def get_character(
    character_id: uuid.UUID,
    service: CharacterService = Depends(get_character_service),
    current_user: User = Depends(get_current_user),
):
    result = service.get_character_detail(current_user.id, character_id)
    if not result:
        raise HTTPException(status_code=404, detail="Character not found")
    if result.status == "locked":
        raise HTTPException(status_code=403, detail="Character is locked!")
    return result



