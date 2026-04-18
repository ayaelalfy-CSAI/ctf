from pydantic import BaseModel
from typing import Optional

class CharacterCreate(BaseModel):
    title: str
    strength: str = "EASY"
    persona: str
    persona_desc: Optional[str] = None
    target: str
    category: Optional[str] = None
    secret: str
    success_msg: Optional[str] = None
    prompt_template: str
    order_index: int = 1
    points_reward: int = 10

class CharacterResponse(BaseModel):
    id: str
    title: str
    strength: str
    persona: str
    persona_desc: Optional[str]
    target: str
    category: Optional[str]
    success_msg: Optional[str]
    order_index: int
    points_reward: int
    is_unlocked: bool

    class Config:
        from_attributes = True