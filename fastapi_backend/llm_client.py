import requests

OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL = "phi3:mini"

SYSTEM_PROMPT = """
You are a CRM support assistant.

Response guidelines:
- Explain information provided by the system 
- Guide the user on next steps
- Be friendly and conversational for greetings and small talk
- Be professional and concise for support-related questions
- Do not describe yourself or your limitations
- If a short response is sufficient, keep it short. (1-2 lines)

If the message is casual, respond casually.
If the message is support-related, respond professionally.

Rules:
- You do NOT access databases or user records
- You do NOT invent facts
- If data is missing, say what is needed

Respond in plain text.
"""

def generate_llm_reply(user_text: str, context: dict) -> str:
    prompt = f"""{SYSTEM_PROMPT}

Context:
{context}

User:
{user_text}
"""

    payload = {
        "model": MODEL,
        "prompt": prompt,
        "stream": False
    }

    try:
        r = requests.post(OLLAMA_URL, json=payload, timeout=30)
        r.raise_for_status()
        return r.json()["response"].strip()
    except Exception as e:
        print("OLLAMA ERROR:", e)
        return "I’m here to help. Could you please rephrase your question?"
