import uuid
from pydantic import BaseModel
from typing import Any
 
 
class ChatRequest(BaseModel):
    character_id: uuid.UUID
    message: str
 
 
class CompletionResult(BaseModel):
    completed: bool
    new_points: int | None = None
 
 
class ChatResponse(BaseModel):
    reply: str | None
    is_compromised: bool
    secret_revealed: str | None = None
    blocked_by_arabguard: bool = False
    completion: CompletionResult | None = None
    next_character_id: str | None = None
    error: str | None = None
