import uuid
import random
from groq import Groq
from core.config import settings
from repositories.character_repository import CharacterRepository
from repositories.progress_repository import ProgressRepository
from repositories.threat_log_repository import ThreatLogRepository
from services.analyzer_service import analyze_prompt, get_blocked_message
from schemas.chat_schema import ChatResponse, CompletionResult

groq_client = Groq(api_key=settings.GROQ_API_KEY)

MODELS_TO_TRY = [
    "llama-3.3-70b-versatile",
    "llama-3.3-70b-specdec",
    "llama-3.1-8b-instant",
    "llama-3.2-3b-preview",
    "mixtral-8x7b-32768",
]


class ChatService:

    def __init__(
        self,
        character_repo: CharacterRepository,
        progress_repo: ProgressRepository,
        threat_log_repo: ThreatLogRepository,
    ):
        self.character_repo = character_repo
        self.progress_repo = progress_repo
        self.threat_log_repo = threat_log_repo

    def chat(
        self,
        user_id: uuid.UUID,
        character_id: uuid.UUID,
        user_message: str,
    ) -> ChatResponse:

        # 1. Validate character
        character = self.character_repo.get_by_id(character_id)
        if not character:
            return ChatResponse(reply=None, is_compromised=False, error="not_found")

        # 2. Check access status
        status = self.progress_repo.get_character_status(user_id, character)
        if status == "locked":
            return ChatResponse(reply=None, is_compromised=False, error="locked")
        if status == "completed":
            return ChatResponse(reply=None, is_compromised=False, error="completed")

        # 3. ArabGuard — runs on EVERY prompt
        analysis = analyze_prompt(
            user_input=user_message,
            system_prompt=character.prompt_template,
        )
        is_attack = analysis.get("is_attack", False)

        # ── Build the base log trace ─────────────────────────────────────────
        # Shape matches the requested output:
        # {
        #   "raw_input": "...",
        #   "decision": "safe|blocked|compromised",
        #   "arabguard_decision": "SAFE|BLOCKED|FLAGGED",
        #   "arabguard_trace": { ...full trace from ArabGuard... }
        # }
        base_trace = {
            "arabguard_decision":   analysis.get("decision"),
            "arabguard_confidence": analysis.get("confidence"),
            "arabguard_trace":      analysis.get("arabguard_trace"),  # ← full trace
            "character":            character.persona,
            "target":               character.target,
            "category":             character.secret_category,
        }

        # ── BLOCKED ──────────────────────────────────────────────────────────
        if is_attack:
            self.threat_log_repo.create_log({
                "user_id":        user_id,
                "character_id":   character_id,
                "raw_input":      user_message,
                "model_output":   None,
                "decision":       "blocked",
                "score":          0,
                "is_compromised": False,
                "trace": {
                    **base_trace,
                    "blocked": True,
                },
            })
            return ChatResponse(
                reply=get_blocked_message(),
                is_compromised=False,
                blocked_by_arabguard=True,
            )

        # 4. Pick random secret
        pool = settings.SECRET_POOL.get(
            character.secret_category,
            settings.SECRET_POOL.get("apartment_numbers", ["101"]),
        )
        target_secret = random.choice(pool)

        # 5. Build system prompt
        system_prompt = character.prompt_template.replace("{secret}", target_secret)

        # 6. LLM call
        model_output = self._get_llm_response(system_prompt, user_message)

        # 7. Compromise check
        is_compromised = target_secret.lower() in model_output.lower()

        next_character = None
        completion_result = None

        if is_compromised:
            next_character = self.character_repo.get_by_level(character.level + 1)
            raw_result = self.progress_repo.complete_character(user_id, character_id)
            completion_result = CompletionResult(**raw_result)
            decision = "compromised"
            score = 100
        else:
            decision = "safe"
            score = 0

        # ── Log every safe / compromised prompt ──────────────────────────────
        self.threat_log_repo.create_log({
            "user_id":        user_id,
            "character_id":   character_id,
            "raw_input":      user_message,
            "model_output":   model_output,
            "decision":       decision,
            "score":          score,
            "is_compromised": is_compromised,
            "trace": {
                **base_trace,
                "secret_used": target_secret if is_compromised else None,
                "blocked":     False,
            },
        })

        print(f"[DEBUG] analysis = {analysis}") 
        
        return ChatResponse(
            reply=model_output,
            is_compromised=is_compromised,
            secret_revealed=target_secret if is_compromised else None,
            blocked_by_arabguard=False,
            completion=completion_result,
            next_character_id=str(next_character.id) if next_character else None,
        )

    def _get_llm_response(self, system_prompt: str, user_input: str) -> str:
        for model_name in MODELS_TO_TRY:
            try:
                completion = groq_client.chat.completions.create(
                    model=model_name,
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user",   "content": user_input},
                    ],
                    max_tokens=100,
                    temperature=0.8,
                    top_p=0.9,
                    frequency_penalty=0.6,
                    presence_penalty=0.5,
                )
                return completion.choices[0].message.content
            except Exception as e:
                print(f"[LLM] Model {model_name} failed: {e}")
                continue
        return "يا بيه السيرفر عليه ضغط رهيب، جرب كمان دقيقة!"