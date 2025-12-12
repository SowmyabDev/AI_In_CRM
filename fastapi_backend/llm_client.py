import os
from llama_cpp import Llama

MODEL_PATH = r"C:\models\tinyllama.gguf"

LLM_TEMPERATURE = 0.1
LLM_MAX_TOKENS = 256
LLM_N_CTX = 2048

_llm = None

def _load_llm():
    global _llm
    if _llm is None:
        _llm = Llama(model_path=MODEL_PATH, n_ctx=LLM_N_CTX, temperature=LLM_TEMPERATURE)
    return _llm

SYSTEM_INSTRUCTIONS = """
You are an assistant for an e-commerce website. Follow these rules exactly:
1) You DO NOT have access to user accounts, order systems, or live tracking. If asked about order status, refunds, or specific user data, respond with a short apology and say you cannot access that data here, then provide clear next steps the user can take (e.g., "provide order ID" or "connect to human support"). Do NOT invent any details.
2) Be concise (2-4 sentences) unless asked for more details.
3) If asked for generic policy information (return window, refund timings), answer only with the policy provided to you or fallback to a short canned policy.
4) Do NOT say you "checked" anything. Instead say: "I cannot access your account from here."
5) If you are unsure, ask one precise clarifying question or offer to connect to human support.
6) Avoid repeating the same fallback message; vary phrasing but keep meaning identical.
"""

def generate_llm_reply(user_text: str, max_tokens: int = LLM_MAX_TOKENS) -> str | None:
    """
    Returns a short reply string or None on failure.
    The prompt format includes SYSTEM_INSTRUCTIONS to minimize hallucination.
    """
    try:
        model = _load_llm()
        prompt = f"{SYSTEM_INSTRUCTIONS}\n\nUser: {user_text}\nAssistant:"
        resp = model(prompt, max_tokens=max_tokens, temperature=LLM_TEMPERATURE, stop=["\nUser:", "\nAssistant:"])
        text = None
        try:
            text = resp.get("choices", [{}])[0].get("text") or resp.get("text")
        except Exception:
            text = None
        if not text:
            return None
        return text.strip()
    except Exception as e:
        return None
