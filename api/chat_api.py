from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from core.database import get_db
from core.deps import get_current_user
from models.user import User
from services.chat_service import chat_with_character
from repositories.progress_repository import get_character_status
from repositories.character_repository import get_character_by_id
import uuid

router = APIRouter(prefix="/chat", tags=["Chat"])

class ChatRequest(BaseModel):
    character_id: uuid.UUID
    message: str

@router.post("/")
def chat(
    body: ChatRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # جيب الشخصية
    character = get_character_by_id(db, body.character_id)
    if not character:
        raise HTTPException(status_code=404, detail="Character not found")

    # اتحقق من الـ status
    status = get_character_status(db, current_user.id, character)
    if status == "locked":
        raise HTTPException(status_code=403, detail="Character is locked!")
    if status == "completed":
        raise HTTPException(status_code=400, detail="Character already completed!")

    result = chat_with_character(
        db=db,
        user_id=current_user.id,
        character_id=body.character_id,
        user_message=body.message
    )

    return result