from sqlalchemy.orm import Session
from anthropic import Anthropic
from core.config import settings
from repositories.character_repository import get_character_by_id
from repositories.threat_log_repository import create_log
from repositories.progress_repository import complete_character
import uuid

client = Anthropic(api_key=settings.ANTHROPIC_API_KEY)

def chat_with_character(
    db: Session,
    user_id: uuid.UUID,
    character_id: uuid.UUID,
    session_id: str,
    user_message: str
):
    # جيب الشخصية
    character = get_character_by_id(db, character_id)
    if not character:
        return None

    # جهّز الـ system prompt مع السر
    system_prompt = character.prompt_template.format(secret=character.secret)

    # كلم الـ AI model
    response = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=1000,
        system=system_prompt,
        messages=[{"role": "user", "content": user_message}]
    )

    model_output = response.content[0].text

    # اكتشف لو اليوزر كسر الشخصية
    is_compromised = character.secret.lower() in user_message.lower() or \
                     character.secret.lower() in model_output.lower()

    # احسب الـ score
    score = 100 if is_compromised else 0

    # سجل في الـ ThreatLog
    create_log(db, {
        "user_id": user_id,
        "character_id": character_id,
        "session_id": session_id,
        "raw_input": user_message,
        "model_output": model_output,
        "decision": "compromised" if is_compromised else "safe",
        "score": score,
        "is_compromised": is_compromised,
        "trace": {
            "character": character.persona,
            "target": character.target,
        }
    })

    # لو كسرها اعمل complete
    if is_compromised:
        complete_character(db, user_id, character_id)

    return {
        "reply": model_output,
        "is_compromised": is_compromised,
        "score": score
    }