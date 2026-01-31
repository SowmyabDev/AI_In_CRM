import requests

OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL_NAME = "phi3"

SYSTEM_PROMPT = """
You are a professional CRM support assistant.

Rules:
- Be polite, concise, and helpful
- You may answer general questions like policies, help, greetings and engage in small talk
- Do NOT guess order, delivery, refund, or cart data
- If the question is unclear, ask for clarification
"""

def generate_llm_reply(text: str) -> str:
    prompt = f"""{SYSTEM_PROMPT}

User: {text}
Assistant:"""

    try:
        response = requests.post(
            OLLAMA_URL,
            json={
                "model": MODEL_NAME,
                "prompt": prompt,
                "stream": False
            },
            timeout=30
        )

        data = response.json()
        return data.get("response", "").strip() or (
            "I’m here to help! Could you please clarify your question?"
        )

    except Exception:
        return (
            "I can help with general questions like policies or guidance. "
            "Please let me know how I can assist."
        )
