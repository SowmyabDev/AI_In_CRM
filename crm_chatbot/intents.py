INTENTS = {
    "greet": ["hi", "hello", "hey"],
    "my_orders": ["Orders","my orders", "order history"],
    "delivery_status": ["delivery","deliveries", "where is my order"],
    "show_cart": ["cart"],
    "wishlist": ["wishlist"],
    "return_request": ["return"],
    "refund_query": ["refund"],
    "goodbye": ["bye", "thanks", "Thank you"]
}

ESCALATION_INTENTS = {
    "human_agent": [
        "agent",
        "human agent",
        "connect me to human",
        "talk to agent",
        "customer support",
        "support executive"
    ]
}


def detect_intent(text: str) -> str:
    text = text.lower()

    for intent, keys in ESCALATION_INTENTS.items():
        if any(k in text for k in keys):
            return intent

    for intent, keys in INTENTS.items():
        if any(k in text for k in keys):
            return intent

    return "unknown"
