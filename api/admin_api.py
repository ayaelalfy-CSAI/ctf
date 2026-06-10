import shutil
import uuid
from fastapi import APIRouter, Depends, Query, UploadFile, File, HTTPException
from sqlalchemy.orm import Session

import shutil
from pathlib import Path

from core.database import get_db
from core.deps import get_admin_user
from models.user import User
from repositories.character_repository import CharacterRepository
from repositories.threat_log_repository import ThreatLogRepository
from services.character_service import CharacterService
from schemas.character_schema import CharacterCreate, CharacterAdminResponse

router = APIRouter(prefix="/admin", tags=["Admin"])

AVATARS_DIR = Path("avatars")
ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp"}


def get_character_service(db: Session = Depends(get_db)) -> CharacterService:
    return CharacterService(character_repo=CharacterRepository(db))


def get_threat_log_repo(db: Session = Depends(get_db)) -> ThreatLogRepository:
    return ThreatLogRepository(db)


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



# ------------------------------------------------------------------
# Avatar upload
# ------------------------------------------------------------------
 
@router.post("/upload-avatar")
def upload_avatar(
    file: UploadFile = File(...),
    admin: User = Depends(get_admin_user),
):
    """
    Upload a character avatar image.
    Returns the URL to use in the avatar field when creating a character.
    Allowed: .jpg / .jpeg / .png / .webp
    """
    # Validate extension
    ext = Path(file.filename).suffix.lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"File type '{ext}' not allowed. Use: {ALLOWED_EXTENSIONS}",
        )
 
    # Use original filename (or generate unique name to avoid collisions)
    filename = f"{uuid.uuid4().hex}{ext}"
    save_path = AVATARS_DIR / filename
 
    # Save file
    AVATARS_DIR.mkdir(exist_ok=True)
    with save_path.open("wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
 
    return {
        "filename": filename,
        "avatar_url": f"http://127.0.0.1:8000/avatars/{filename}",
    }
 



@router.get("/threat-logs")
def get_threat_logs_dashboard(
    limit: int = Query(100, ge=1, le=500),
    offset: int = Query(0, ge=0),
    repo: ThreatLogRepository = Depends(get_threat_log_repo),
    admin: User = Depends(get_admin_user),
):
    logs = repo.get_all_logs(limit=limit, offset=offset)
    return {
        "logs": [_serialize_log(log) for log in logs],
    }


def _serialize_log(log) -> dict:
    trace = log.trace or {}
    return {
        "raw_input":          log.raw_input,
        "model_output":       log.model_output,
        "decision":           log.decision,
        "is_compromised":     log.is_compromised,
        "arabguard_decision": trace.get("arabguard_decision"),
        "arabguard_trace":    trace.get("arabguard_trace"),
        "character":          trace.get("character"),
        "target":             trace.get("target"),
        "blocked":            trace.get("blocked", False),
    }