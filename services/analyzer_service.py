from gradio_client import Client
import random

BLOCKED_MESSAGES = [
    "🚨 تم اكتشاف محاولة اختراق! حاول بأسلوب تاني يا شاطر 😏",
    "⛔ النظام شايفك! مش هينفع الكلام ده هنا 👀",
    "🛡️ ArabGuard قفشك! جرب تفكر بطريقة تانية 🤔",
    "❌ محاولة محجوبة! ده مش هيعدي من هنا 😄",
    "🔒 تم رصد هجوم! النظام أذكى منك بكتير 😎",
    "⚠️ Prompt Injection مش هينفع معانا يا صديقي!",
    "🤖 ArabGuard V2 يقول: Nice try, but no! 😂",
]

def get_ag_client():
    try:
        return Client("d12o6aa/ArabGuard-Analyzer")
    except Exception as e:
        print(f"Error connecting to ArabGuard: {e}")
        return None

def analyze_prompt(user_input: str, system_prompt: str = "أنت مساعد ذكي.") -> dict:
    client = get_ag_client()
    if not client:
        return {"is_attack": False, "confidence": 0.0, "decision": "SAFE"}

    try:
        result = client.predict(
            user_input=user_input,
            system_prompt=system_prompt,
            api_name="/universal_api"  # ✅ الاسم الصح
        )

        # result = (status_message, arabguard_trace, security_decision)
        status_message = result[0]
        arabguard_trace = result[1]
        security_decision = result[2]

        print("STATUS MESSAGE:", status_message)
        print("TRACE:", arabguard_trace)
        print("DECISION:", security_decision)

        # security_decision هو dict فيه label
        label = security_decision.get("label", "SAFE") if isinstance(security_decision, dict) else str(security_decision)
        is_attack = "BLOCKED" in str(label).upper() or "FLAG" in str(label).upper()

        confidences = security_decision.get("confidences", []) if isinstance(security_decision, dict) else []
        confidence = next((c["confidence"] for c in confidences if c["label"] == label), 0.0) if confidences else 0.0

        return {
            "is_attack": is_attack,
            "decision": label,
            "confidence": confidence,
            "source": "arabguard"
        }

    except Exception as e:
        print(f"Analysis error: {e}")
        return {"is_attack": False, "confidence": 0.0, "decision": "SAFE"}

def get_blocked_message() -> str:
    return random.choice(BLOCKED_MESSAGES)