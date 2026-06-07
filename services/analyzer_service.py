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
 
_SAFE_RESPONSE = {"is_attack": False, "confidence": 0.0, "decision": "SAFE"}
 
 
def _get_ag_client() -> Client | None:
    """إنشاء connection لـ ArabGuard — بيرجع None لو فشل."""
    try:
        return Client("d12o6aa/ArabGuard-Analyzer")
    except Exception as e:
        print(f"[ArabGuard] Connection error: {e}")
        return None
 
 
def _parse_decision(security_decision) -> tuple[str, float]:
    """
    استخرج الـ label والـ confidence من الـ security_decision.
    بيرجع (label, confidence).
    """
    if not isinstance(security_decision, dict):
        return str(security_decision), 0.0
 
    label = security_decision.get("label", "SAFE")
    confidences = security_decision.get("confidences", [])
    confidence = next(
        (c["confidence"] for c in confidences if c["label"] == label),
        0.0,
    )
    return label, confidence
 
 
def analyze_prompt(user_input: str, system_prompt: str = "أنت مساعد ذكي.") -> dict:
    """
    بيبعت الـ prompt لـ ArabGuard ويرجع:
    {
        "is_attack": bool,
        "decision": str,   # "SAFE" | "BLOCKED" | "FLAGGED"
        "confidence": float,
        "source": "arabguard"
    }
    لو الـ connection فشل بيرجع SAFE عشان ما يوقفش الـ flow.
    """
    client = _get_ag_client()
    if not client:
        return _SAFE_RESPONSE
 
    try:
        # result = (status_message, arabguard_trace, security_decision)
        result = client.predict(
            user_input=user_input,
            system_prompt=system_prompt,
            api_name="/universal_api",
        )
 
        status_message, arabguard_trace, security_decision = result
 
        print(f"[ArabGuard] Status:   {status_message}")
        print(f"[ArabGuard] Trace:    {arabguard_trace}")
        print(f"[ArabGuard] Decision: {security_decision}")
 
        label, confidence = _parse_decision(security_decision)
        is_attack = "BLOCKED" in str(label).upper() or "FLAG" in str(label).upper()
 
        return {
            "is_attack": is_attack,
            "decision": label,
            "confidence": confidence,
            "source": "arabguard",
        }
 
    except Exception as e:
        print(f"[ArabGuard] Analysis error: {e}")
        return _SAFE_RESPONSE
 
 
def get_blocked_message() -> str:
    """بيرجع رسالة حجب عشوائية."""
    return random.choice(BLOCKED_MESSAGES)
 
