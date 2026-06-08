import random
from gradio_client import Client

BLOCKED_MESSAGES = [
    "🚨 تم اكتشاف محاولة اختراق! حاول بأسلوب تاني يا شاطر 😏",
    "⛔ النظام شايفك! مش هينفع الكلام ده هنا 👀",
    "🛡️ ArabGuard قفشك! جرب تفكر بطريقة تانية 🤔",
    "❌ محاولة محجوبة! ده مش هيعدي من هنا 😄",
    "🔒 تم رصد هجوم! النظام أذكى منك بكتير 😎",
    "⚠️ Prompt Injection مش هينفع معانا يا صديقي!",
    "🤖 ArabGuard V2 يقول: Nice try, but no! 😂",
]

_SAFE_RESULT = {
    "is_attack":        False,
    "decision":         "SAFE",
    "confidence":       0.0,
    "source":           "arabguard",
    "arabguard_trace":  None,
}


def _get_ag_client() -> Client | None:
    try:
        return Client("d12o6aa/ArabGuard-Analyzer")
    except Exception as e:
        print(f"[ArabGuard] Connection error: {e}")
        return None


def _parse_decision(security_decision) -> tuple[str, float]:
    if not isinstance(security_decision, dict):
        return str(security_decision), 0.0

    label = security_decision.get("label", "SAFE")
    confidences = security_decision.get("confidences") or []  # ← None → []

    confidence = next(
        (c["confidence"] for c in confidences if c["label"] == label),
        0.0,
    )
    return label, confidence


def analyze_prompt(user_input: str, system_prompt: str = "أنت مساعد ذكي.") -> dict:
    client = _get_ag_client()
    if not client:
        return _SAFE_RESULT

    try:
        result = client.predict(
            user_input=user_input,
            system_prompt=system_prompt,
            api_name="/universal_api",
        )
        status_message, arabguard_trace, security_decision = result

        print(f"[ArabGuard] Status:   {status_message}")
        print(f"[ArabGuard] Decision: {security_decision}")
        print(f"[ArabGuard] Trace:    {arabguard_trace}")

        label, confidence = _parse_decision(security_decision)
        is_attack = "BLOCKED" in str(label).upper() or "FLAG" in str(label).upper()

        return {
            "is_attack":       is_attack,
            "decision":        label,
            "confidence":      confidence,
            "source":          "arabguard",
            "arabguard_trace": arabguard_trace,  # ← الـ trace الكامل
        }

    except Exception as e:
        print(f"[ArabGuard] Analysis error: {e}")
        return _SAFE_RESULT


def get_blocked_message() -> str:
    return random.choice(BLOCKED_MESSAGES)