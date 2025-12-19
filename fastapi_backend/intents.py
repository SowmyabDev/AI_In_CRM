INTENT_PATTERNS = {
    "greet": ["hi", "hello", "hey"],
    "goodbye": ["bye", "thank you", "thanks"],
    "ack": ["ok", "okay", "sure", "fine"],

    "my_orders": ["my orders", "order history", "list orders"],
    "order_status": ["order status", "track order"],

    "show_cart": ["show cart", "my cart"],
    "add_to_cart": ["add to cart", "add"],
    "remove_from_cart": ["remove", "delete"],
    
    "return_request": ["return", "replace"],
    "refund_query": ["refund"],
    "complaint": ["complaint", "issue", "problem"],

    "human_handoff": [
        "human",
        "agent",
        "talk to human",
        "connect me",
        "support",
        "customer care"
    ],

}

def detect_intent(text: str) -> str:
    t = text.lower()
    for intent, patterns in INTENT_PATTERNS.items():
        for p in patterns:
            if p in t:
                return intent
    return "unknown"
