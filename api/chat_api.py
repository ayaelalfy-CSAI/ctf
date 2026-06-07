from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
 
from core.database import get_db
from core.deps import get_current_user
from models.user import User
from repositories.character_repository import CharacterRepository
from repositories.progress_repository import ProgressRepository
from repositories.threat_log_repository import ThreatLogRepository
from services.chat_service import ChatService
from schemas.chat_schema import ChatRequest, ChatResponse
 
router = APIRouter(prefix="/chat", tags=["Chat"])
 
 
def get_chat_service(db: Session = Depends(get_db)) -> ChatService:
    return ChatService(
        character_repo=CharacterRepository(db),
        progress_repo=ProgressRepository(db),
        threat_log_repo=ThreatLogRepository(db),
    )
 
 
@router.post("/", response_model=ChatResponse)
def chat(
    body: ChatRequest,
    service: ChatService = Depends(get_chat_service),
    current_user: User = Depends(get_current_user),
):
    result = service.chat(
        user_id=current_user.id,
        character_id=body.character_id,
        user_message=body.message,
    )
 
    # Translate service-level errors into proper HTTP responses
    if result.error == "not_found":
        raise HTTPException(status_code=404, detail="Character not found")
    if result.error == "locked":
        raise HTTPException(status_code=403, detail="Character is locked!")
    if result.error == "completed":
        raise HTTPException(status_code=400, detail="Character already completed!")
 
    return result
