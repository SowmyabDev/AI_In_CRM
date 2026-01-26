INTENTS = {
    "greet": ["hi", "hello", "hey"],
    "my_orders": ["my orders", "order history", "list my orders"],
    "delivery_status": ["delivery", "deliveries", "where is my order", "list my deliveries"],
    "show_cart": ["cart"],
    "wishlist": ["wishlist"],
    "return_request": ["return"],
    "refund_query": ["refund"],
    "human_agent": [
        "agent"
        "human agent",
        "connect me to human",
        "talk to agent",
        "customer support",
        "support executive"
    ],
    "goodbye": ["bye", "thanks", "thank you"]
}

def detect_intent(text: str) -> str:
    text = text.lower()
    for intent, keys in INTENTS.items():
        if any(k in text for k in keys):
            return intent
    return "unknown"
