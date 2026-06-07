import uuid
from pydantic import BaseModel
from typing import Optional
 
 
class CharacterProgressResponse(BaseModel):
    id: uuid.UUID
    persona: str
    persona_desc: str
    avatar: Optional[str]
    target: str
    level: int
    points_required: int
    status: str  # "active" | "locked" | "completed"
 
    class Config:
        from_attributes = True
 
 
class CompleteCharacterResponse(BaseModel):
    message: str
    points_added: int
    total_points: Optional[int] = None
 
 
class MyPointsResponse(BaseModel):
    points: int
    name: str
    photo: Optional[str]
