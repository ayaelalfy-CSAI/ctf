import uuid
from pydantic import BaseModel
from typing import Optional
 
 
# ─── Input ────────────────────────────────────────────────────────────────────
 
class CharacterCreate(BaseModel):
    title: str
    level: int
    persona: str
    persona_desc: str
    target: str
    secret_category: str
    success_msg: str
    prompt_template: str
    points_required: int
    points_reward: int
    avatar: Optional[str] = None
 
 
# ─── Admin responses (full data, no user-specific fields) ─────────────────────
 
class CharacterAdminResponse(BaseModel):
    id: uuid.UUID
    title: str
    level: int
    persona: str
    persona_desc: str
    target: str
    secret_category: str
    success_msg: str
    prompt_template: str
    points_required: int
    points_reward: int
    avatar: Optional[str] = None
 
    class Config:
        from_attributes = True
 
 
# ─── User responses (no sensitive fields like prompt_template) ────────────────
 
class CharacterUserResponse(BaseModel):
    id: uuid.UUID
    title: str
    level: int
    persona: str
    persona_desc: str
    target: str
    avatar: Optional[str] = None
    points_required: int
    points_reward: int
    status: str  # "active" | "locked" | "completed"
 
    class Config:
        from_attributes = True


class CharacterListItem(BaseModel):
    id: uuid.UUID
    title: str
    persona_desc: str
    avatar: Optional[str] = None
    status: str

    class Config:
        from_attributes = True        
 
