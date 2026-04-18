from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from core.database import get_db
from core.deps import get_current_user
from models.user import User
from services.chat_service import chat_with_character
from repositories.progress_repository import is_character_unlocked
import uuid

router = APIRouter(prefix="/chat", tags=["Chat"])

class ChatRequest(BaseModel):
    character_id: uuid.UUID
    session_id: str
    message: str

@router.post("/")
def chat(
    body: ChatRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if not is_character_unlocked(db, current_user.id, body.character_id):
        raise HTTPException(status_code=403, detail="Character is locked!")

    result = chat_with_character(
        db=db,
        user_id=current_user.id,
        character_id=body.character_id,
        session_id=body.session_id,
        user_message=body.message
    )

    if not result:
        raise HTTPException(status_code=404, detail="Character not found")

    return result