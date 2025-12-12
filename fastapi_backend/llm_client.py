import json
import os
from typing import Optional

try:
    from llama_cpp import Llama
    _HAS_LLAMA = True
except Exception:
    _HAS_LLAMA = False

MODEL_PATH = os.environ.get("LLM_MODEL_PATH", r"C:\models\tinyllama.gguf")

_llm = None
if _HAS_LLAMA:
    try:
        _llm = Llama(model_path=MODEL_PATH, n_ctx=2048, temperature=0.2)
    except Exception:
        _llm = None
        _HAS_LLAMA = False

SYSTEM_PROMPT = """
You are a professional, concise e-commerce support assistant. Tone: short, formal, businesslike.
Instructions:
- Use the provided 'intent' and 'context' to craft one short reply (1-3 sentences).
- Do NOT invent or assume order-specific details (tracking numbers, dates, delivery times).
- If the intent is about policy (returns/refunds/delivery), explain the policy concisely.
- If you cannot produce a safe answer, return an empty string.
Return plain text (no JSON).
"""

def generate_reply(intent: str, user_text: str, context: dict) -> Optional[str]:
    """
    Return a short plain-text reply (business tone) or None if LLM unavailable or failed.
    LLM should NOT decide escalation. It only formulates wording.
    """

    if not _HAS_LLAMA or _llm is None:
        return None

    prompt = f"""{SYSTEM_PROMPT}

Intent: {intent}
Context: {json.dumps(context)}
User message: {user_text}

Provide a short (1-3 sentences), businesslike reply.
"""
    try:
        resp = _llm(prompt, max_tokens=120)
        text = (resp.get("choices") or [{}])[0].get("text") or resp.get("text")
        if not text:
            return None
        return text.strip().replace("\n", " ")
    except Exception:
        return None

def canned_reply(intent: str) -> str:
    if intent in ("returns", "return_request"):
        return "Most items can be returned within 7 days of delivery. Please provide your order ID to start a return or I can connect you to support."
    if intent in ("refund", "refund_query"):
        return "Refunds are processed within 3–5 business days after the return is received."
    if intent in ("delivery", "delivery_query"):
        return "Typical delivery time is 2–5 business days depending on location. I cannot view order-specific delivery dates."
    if intent == "greet":
        return "Hello. How can I assist you?"
    if intent == "search":
        return "Please provide keywords or say 'search <term>' and I will look up products."
    return ""
