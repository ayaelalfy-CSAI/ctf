from pydantic import BaseModel
from datetime import datetime
from typing import List

class CompletedLevelSchema(BaseModel):
    character_id: str
    title: str
    persona: str
    strength: str
    points_reward: int
    completed_at: datetime

class UserMeResponse(BaseModel):
    id: str
    name: str
    photo: str | None
    role: str
    points: int
    rank: int | None
    total_players: int
    completed_levels_count: int
    completed_levels: List[CompletedLevelSchema]