"""Intent detection using regex pattern matching for e-commerce chatbot.
Classifies queries as resolvable (chatbot) or escalatable (human).
"""

from typing import Dict, List, Set
import re


# Intents the chatbot can resolve directly
RESOLVABLE_INTENTS: Set[str] = {
    "greet", "goodbye", "ack",
    "browse_products", "search_products", "product_details",
    "show_cart", "add_to_cart", "remove_from_cart", "clear_cart",
    "my_orders", "order_status", "track_shipment",
    "recommendations", "promotions"
}

# Intents that require human escalation
ESCALATABLE_INTENTS: Set[str] = {
    "return_request", "refund_query", "complaint",
    "checkout", "payment",
    "account", "address", "wishlist",
    "shipping", "human_handoff"
}

# Regex patterns for each intent
RAW_INTENT_PATTERNS: Dict[str, List[str]] = {
    "greet": ["hi", "hello", "hey"],
    "goodbye": ["bye", "thank you", "thanks"],
    "ack": ["ok", "okay", "sure", "fine"],

    # Order-related
    "my_orders": ["my orders", "order history", "list orders", "show orders", "current orders", "what are my orders"],
    "order_status": ["order status", "track order", "where is my order", "order tracking"],
    "return_request": ["return", "replace", "return order"],
    "refund_query": ["refund", "refund status"],
    "complaint": ["complaint", "issue", "problem", "not working"],

    # Product browsing
    "browse_products": ["show products", "what products", "browse", "product list", "all products", "available items"],
    "search_products": ["search for", "find product", "do you have", "look for"],
    "product_details": ["price", "cost", "details", "description", "specification", "specs"],

    # Cart management
    "show_cart": ["show cart", "my cart", "cart items", "what's in my cart"],
    "add_to_cart": ["add to cart", "add", "add item", "buy"],
    "remove_from_cart": ["remove from cart", "remove", "delete from cart"],
    "clear_cart": ["clear cart", "empty cart"],

    # Checkout & payment
    "checkout": ["checkout", "place order", "buy now", "proceed to payment"],
    "shipping": ["shipping", "delivery", "how long", "shipping cost", "delivery time"],
    "payment": ["payment", "pay", "credit card", "cash on delivery"],

    # Account & Profile
    "account": ["account", "profile", "my details", "change password", "update info"],
    "address": ["address", "shipping address", "delivery address"],
    "wishlist": ["wishlist", "save for later", "favorites"],

    # Recommendations & Help
    "recommendations": ["recommend", "suggest", "best selling", "popular"],
    "promotions": ["discount", "coupon", "promo", "deal", "sale"],
    "track_shipment": ["track shipment", "shipment status"],

    # Support escalation
    "human_handoff": [
        "human",
        "agent",
        "talk to human",
        "connect me",
        "support",
        "customer care",
    ],
}

# Compile regex patterns for efficiency
COMPILED_PATTERNS: Dict[str, List[re.Pattern]] = {
    intent: [re.compile(r"\b" + re.escape(pat) + r"\b", re.IGNORECASE) for pat in pats]
    for intent, pats in RAW_INTENT_PATTERNS.items()
}


def detect_intent(text: str) -> str:
    """
    Detect the intent of a user message using regex patterns.
    Returns the intent string or 'unknown'.
    """
    for intent, patterns in COMPILED_PATTERNS.items():
        for pat in patterns:
            if pat.search(text):
                return intent
    return "unknown"