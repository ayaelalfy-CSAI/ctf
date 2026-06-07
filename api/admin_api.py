import uuid
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
 
from core.database import get_db
from core.deps import get_admin_user
from models.user import User
from repositories.character_repository import CharacterRepository
from services.character_service import CharacterService
from schemas.character_schema import CharacterCreate, CharacterAdminResponse
 
router = APIRouter(prefix="/admin", tags=["Admin"])
 
 
def get_character_service(db: Session = Depends(get_db)) -> CharacterService:
    return CharacterService(character_repo=CharacterRepository(db))
 
 
@router.post("/characters")
def create_character(
    body: CharacterCreate,
    service: CharacterService = Depends(get_character_service),
    admin: User = Depends(get_admin_user),
):
    return service.create_character(body)
 
 
@router.get("/characters", response_model=list[CharacterAdminResponse])
def get_all_characters(
    service: CharacterService = Depends(get_character_service),
    admin: User = Depends(get_admin_user),
):
    return service.get_all_characters()
 
 
@router.put("/characters/{character_id}")
def update_character(
    character_id: uuid.UUID,
    body: CharacterCreate,
    service: CharacterService = Depends(get_character_service),
    admin: User = Depends(get_admin_user),
):
    return service.update_character(character_id, body)
 
 
@router.delete("/characters/{character_id}")
def delete_character(
    character_id: uuid.UUID,
    service: CharacterService = Depends(get_character_service),
    admin: User = Depends(get_admin_user),
):
    return service.delete_character(character_id)
 
