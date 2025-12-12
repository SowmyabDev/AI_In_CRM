import re
from product_data import products

FAQ = {
    "returns": "You can return most items within 7 days of delivery.",
    "refund": "Refunds are processed within 3–5 business days after pickup.",
    "delivery": "Delivery usually takes 2–5 business days depending on location."
}

INTENT_PATTERNS = {
    "greet": ["hi", "hello", "hey"],
    "order_status": ["order status", "track", "where is my order", "active orders"],
    "returns": ["return", "send back", "return policy"],
    "refund": ["refund", "money back"],
    "cancel": ["cancel"],
    "delivery": ["when will", "delivery", "arrive"],
    "recommend": ["recommend", "suggest", "best"],
    "search": ["search", "find", "look for"],
    "show_cart": ["show cart", "my cart"],
    "add_to_cart": ["add"],
    "remove_from_cart": ["remove"],
    "human": ["human", "agent", "support"],
}

def detect_intent(text):
    t = text.lower()
    for intent, patterns in INTENT_PATTERNS.items():
        if any(p in t for p in patterns):
            return intent

    if "product" in t and re.search(r"\b\d+\b", t):
        return "product_info"

    return "unknown"

def search_products(query):
    q = query.lower()
    return [p for p in products if q in p["name"].lower() or q in p["category"].lower()]

def product_details(pid):
    for p in products:
        if p["id"] == pid:
            return p
    return None
