from crm_chatbot.intents import detect_intent, INTENTS, ESCALATION_INTENTS
from crm_chatbot.llm_client import generate_llm_reply


def chatbot_resolves_query(user_text: str) -> bool:
    """
    Core chatbot resolution logic.
    Returns:
        True  -> resolved by chatbot
        False -> escalation required
    """

    intent = detect_intent(user_text)

    if intent in ESCALATION_INTENTS:
        return False

    if intent in INTENTS:
        return True

    reply = generate_llm_reply(user_text).lower()

    if "support" in reply or "agent" in reply or "escalate" in reply:
        return False

    return False
