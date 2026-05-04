from sqlalchemy.orm import Session
from groq import Groq
from core.config import settings
from repositories.character_repository import get_character_by_id
from repositories.threat_log_repository import create_log
from repositories.progress_repository import complete_character, get_character_status
from services.analyzer_service import analyze_prompt, get_blocked_message
import uuid
import random

groq_client = Groq(api_key=settings.GROQ_API_KEY)

MODELS_TO_TRY = [
    "llama-3.3-70b-versatile",
    "llama-3.3-70b-specdec",
    "llama-3.1-8b-instant",
    "llama-3.2-3b-preview",
    "mixtral-8x7b-32768"
]

def get_llm_response(system_prompt: str, user_input: str) -> str:
    for model_name in MODELS_TO_TRY:
        try:
            completion = groq_client.chat.completions.create(  
                model=model_name,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_input},
                ],
                max_tokens=100,
                temperature=0.8,
                top_p=0.9,
                frequency_penalty=0.6,
                presence_penalty=0.5
            )
            return completion.choices[0].message.content
        except Exception as e:
            print(f"Model {model_name} failed: {e}")
            continue
    return "يا بيه السيرفر عليه ضغط رهيب، جرب كمان دقيقة!"

def chat_with_character(
    db: Session,
    user_id: uuid.UUID,
    character_id: uuid.UUID,
    session_id: str,
    user_message: str
):
    # 1. جيب الشخصية
    character = get_character_by_id(db, character_id)
    if not character:
        return None

    # 2. تأكد إن الـ status active
    status = get_character_status(db, user_id, character)
    if status == "locked":
        return {"error": "locked", "reply": None, "is_compromised": False}
    if status == "completed":
        return {"error": "completed", "reply": None, "is_compromised": False}

    # 3. ArabGuard + Manual Filter
    analysis = analyze_prompt(user_message)
    is_attack = analysis.get("is_attack", False)
    if is_attack:
        return {
            "reply": get_blocked_message(),
            "is_compromised": False,
            "secret_revealed": None,
            "blocked_by_arabguard": True
        }

    # 4. اختار سر عشوائي من الـ pool secret_category
    pool = settings.SECRET_POOL.get(
        character.secret_category,
        settings.SECRET_POOL.get("apartment_numbers", ["101"])
    )
    target_secret = random.choice(pool)

    # 5. جهّز الـ system prompt
    system_prompt = character.prompt_template.replace("{secret}", target_secret)

    # 6. كلم الـ Groq
    model_output = get_llm_response(system_prompt, user_message)

    # 7. اتحقق من الاختراق
    is_compromised = target_secret.lower() in model_output.lower()

    # 8. سجل في ThreatLog بس لو حصل اختراق
    if is_compromised:
        create_log(db, {
            "user_id": user_id,
            "character_id": character_id,
            "session_id": session_id,
            "raw_input": user_message,
            "model_output": model_output,
            "decision": "compromised",
            "score": 100,
            "is_compromised": True,
            "trace": {
                "character": character.persona,
                "target": character.target,         
                "secret_used": target_secret,
                "category": character.secret_category  
            }
        })
        complete_character(db, user_id, character_id)

    return {
        "reply": model_output,
        "is_compromised": is_compromised,
        "secret_revealed": target_secret if is_compromised else None,
        "blocked_by_arabguard": False
    }