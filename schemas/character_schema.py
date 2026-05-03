from pydantic import BaseModel
from typing import Optional

class CharacterCreate(BaseModel):
    title: str
    level: int = 1
    persona: str
    persona_desc: Optional[str] = None
    target: str
    secret_category: str
    success_msg: Optional[str] = None
    prompt_template: str
    points_required: int = 10
    avatar: Optional[str] = None

class CharacterResponse(BaseModel):
    id: str
    title: str
    strength: str
    persona: str
    persona_desc: Optional[str]
    target: str
    category: Optional[str]
    success_msg: Optional[str]
    points_reward: int
    is_unlocked: bool

    class Config:
        from_attributes = True

class CharacterStatusResponse(BaseModel):
    id: str
    persona: str
    avatar: Optional[str]
    status: str  # completed / active / locked

