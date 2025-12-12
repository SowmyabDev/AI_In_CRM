import re
from products_data import products

INTENT_PATTERNS = {
    "greet": ["hi", "hello", "hey", "good morning", "good evening"],
    "goodbye": ["bye", "thank you", "thanks", "thanks!"],

    "order_status": [
        "track", "tracking", "order status", "where is my order", "where is my parcel",
        "missing order", "lost order", "order missing", "delivery status"
    ],

    "delivery_query": [
        "delivery", "arrive", "reach", "ship", "shipping", "when will", "expected"
    ],

    "return_request": [
        "return", "send back", "replace", "exchange", "wrong item", "incorrect item"
    ],

    "refund_query": ["refund", "money back", "reimburse"],

    "complaint": ["complaint", "issue", "problem", "broken", "damaged", "not working"],

    "search": ["search", "find", "look for", "show me", "show"],
    "product_info": ["details", "info on", "information about", "specs"],

    "add_to_cart": ["add", "add to cart"],
    "remove_from_cart": ["remove", "delete", "remove from cart"],
    "show_cart": ["my cart", "show cart", "cart"],

    "my_orders": ["my orders", "order history"],

    "human": ["human", "agent", "support", "help", "contact support"],
    "confirm_escalation": ["yes", "ok", "okay", "sure", "please do", "please"]
}

def detect_intent(text):
    t = text.lower().strip()

    if any(p in t for p in ["connect me", "connect", "escalate", "talk to agent"]):
        return "confirm_escalation"

    if any(p in t for p in ["human", "agent", "support"]):
        return "human"

    if any(p in t for p in ["hi", "hello", "hey"]):
        return "greet"

    if any(p in t for p in ["bye", "thanks", "thank you"]):
        return "goodbye"

    if any(p in t for p in ["my orders", "orders", "order list"]):
        return "my_orders"

    if any(p in t for p in ["track", "order status", "where is my order"]):
        return "order_status"

    if any(p in t for p in ["when will", "delivery", "arrive"]):
        return "delivery_query"

    if any(p in t for p in ["return", "send back"]):
        return "returns"

    if any(p in t for p in ["refund", "money back"]):
        return "refund_query"

    if "add" in t:
        return "add_to_cart"

    if "remove" in t:
        return "remove_from_cart"

    if "cart" in t:
        return "show_cart"

    if any(p in t for p in ["search", "find", "looking for"]):
        return "search"

    if text.lower() in ["ok", "okay", "okay nice", "nice", "cool", "sure", "alright"]:
        return "ack"

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
