import uuid
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
 
from core.database import get_db
from core.deps import get_current_user
from models.user import User
from repositories.character_repository import CharacterRepository
from repositories.progress_repository import ProgressRepository
from services.progress_service import ProgressService
from schemas.progress_schema import (
    CharacterProgressResponse,
    CompleteCharacterResponse,
    MyPointsResponse,
)
 
router = APIRouter(prefix="/progress", tags=["Progress"])
 
 
def get_progress_service(db: Session = Depends(get_db)) -> ProgressService:
    return ProgressService(
        character_repo=CharacterRepository(db),
        progress_repo=ProgressRepository(db),
    )
 
 
@router.post("/complete/{character_id}", response_model=CompleteCharacterResponse)
def complete_character_endpoint(
    character_id: uuid.UUID,
    service: ProgressService = Depends(get_progress_service),
    current_user: User = Depends(get_current_user),
):
    return service.complete_character(current_user.id, character_id)
 
 
@router.get("/characters", response_model=list[CharacterProgressResponse])
def get_characters(
    service: ProgressService = Depends(get_progress_service),
    current_user: User = Depends(get_current_user),
):
    return service.get_characters_with_status(current_user.id)
 
 
@router.get("/my-points", response_model=MyPointsResponse)
def get_my_points(
    current_user: User = Depends(get_current_user),
):
    # لا تحتاج service لأنه بيرجع بيانات الـ user المحمّل أصلاً
    return MyPointsResponse(
        points=current_user.points,
        name=current_user.name,
        photo=current_user.photo,
    )
