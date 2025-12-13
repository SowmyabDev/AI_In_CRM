import re
from products_data import products

INTENT_PATTERNS = {
    "confirm_escalation": [
        "connect me", "connect", "escalate", "talk to agent","human", "agent", "support", "contact support"
    ],

    "greet": [
        "hi", "hello", "hey", "good morning", "good evening"
    ],

    "goodbye": [
        "bye", "thank you", "thanks"
    ],

    "my_orders": [
        "my orders", "order history", "orders", "order list"
    ],

    "order_status": [
        "track", "tracking", "order status",
        "where is my order", "where is my parcel",
        "missing order", "lost order", "order missing"
    ],

    "delivery_query": [
        "delivery", "arrive", "reach", "ship",
        "shipping", "when will", "expected"
    ],

    "return_request": [
        "return", "send back", "replace",
        "exchange", "wrong item", "incorrect item"
    ],

    "refund_query": [
        "refund", "money back", "reimburse"
    ],

    "complaint": [
        "complaint", "issue", "problem",
        "broken", "damaged", "not working"
    ],

    "add_to_cart": [
        "add to cart", "add"
    ],

    "remove_from_cart": [
        "remove from cart", "remove", "delete"
    ],

    "show_cart": [
        "my cart", "show cart", "cart"
    ],

    "search": [
        "search", "find", "look for",
        "looking for", "show me", "show"
    ],

    "product_info": [
        "details", "info on", "information about", "specs"
    ],

    "ack": [
        "ok", "okay", "sure", "alright", "cool", "nice"
    ]
}

def detect_intent(text: str) -> str:
    t = text.lower().strip()

    # Check intents in defined order
    for intent, patterns in INTENT_PATTERNS.items():
        for p in patterns:
            if p in t:
                return intent

    return "unknown"


def extract_order_id(text: str):
    m = re.search(r"\b(ORD[0-9]{3,12})\b", text.upper())
    return m.group(1) if m else None

def extract_product_id(text: str):
    m = re.search(r"\b(\d{2,6})\b", text)
    return int(m.group(1)) if m else None

def search_products(query: str):
    q = query.lower()
    return [p for p in products if q in p["name"].lower() or q in p["category"].lower()]

def product_details(pid: int):
    for p in products:
        if p["id"] == pid:
            return p
    return None
