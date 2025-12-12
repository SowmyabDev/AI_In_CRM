import json
from llama_cpp import Llama

MODEL_PATH = r"C:\models\tinyllama.gguf"

_llm = None

def load_llm():
    global _llm
    if _llm is None:
        _llm = Llama(model_path=MODEL_PATH, n_ctx=2048, temperature=0.1)
    return _llm

INTENT_LIST = [
    "greet", "goodbye", "order_status", "delivery_query", "return_request",
    "refund_query", "complaint", "search", "product_info",
    "add_to_cart", "remove_from_cart", "show_cart", "my_orders",
    "human", "confirm_escalation", "unknown"
]

SYSTEM_PROMPT = f"""
You refine intents for an e-commerce AI assistant.

RULES:
1. You receive a rough intent from keyword detection.
2. You must correct it IF the user message clearly indicates another intent.
3. If the message is unclear, return "unknown".
4. You MUST return valid JSON:
   {{"intent": "<one_of_intents>"}}
Allowed intents: {INTENT_LIST}
"""

def llm_refine_intent(user_text, rough_intent):
    llm = load_llm()

    prompt = f"""
{SYSTEM_PROMPT}

User message: {user_text}
Detected rough intent: {rough_intent}

Respond ONLY with JSON.
"""

    resp = llm(prompt, max_tokens=128)
    raw = resp["choices"][0]["text"].strip()

    try:
        data = json.loads(raw)
        incoming = data.get("intent")
        if incoming in INTENT_LIST:
            return incoming
    except:
        return "unknown"

    return "unknown"
