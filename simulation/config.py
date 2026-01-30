# ================= SIMULATION CONFIG =================

RANDOM_SEED = 42

ARRIVAL_RATE = 0.0002        # avg arrival every 2 minutes
SERVICE_TIME = 1            # avg service time (minutes)
PATIENCE_TIME = 5           # avg patience (minutes)

WORKING_HOURS_MIN = 8 * 60  # 8 hours
MAX_AGENTS = 20

TARGET_AVG_WAIT = 2.0
TARGET_ABANDONMENT = 5.0


# ================= CHATBOT CONFIG =================

# Comprehensive CRM-style chatbot queries
CHATBOT_QUERIES = [

    # ---- Greetings / Small talk ----
    # "hi", "hello", "hey", "good morning", "good evening",
    # "are you there", "can you help me", "thanks", "thank you", "bye",

    # ---- Orders ----
    # "my orders", "order history", "where is my order", "track my order",
    # "order status", "order delayed", "order not delivered",
    # "missing items in my order", "wrong item received",
    # "cancel my order", "order cancelled",

    # ---- Delivery / Shipping ----
    # "delivery status", "shipping status",
    # "when will my order arrive", "delivery failed",
    # "package not received", "change delivery address",

    # ---- Cart / Checkout ----
    # "show my cart", "view cart", "items in my cart",
    # "remove item from cart", "update cart quantity",
    # "checkout issue", "cart not updating",

    # ---- Wishlist ----
    "wishlist", "view wishlist", "remove from wishlist",

    # ---- Returns ----
    # "return my order", "how do i return a product",
    # "return status", "return pickup scheduled",

    # ---- Refunds / Payments ----
    # "refund status", "refund not received",
    # "when will i get my refund", "payment failed",
    # "charged twice", "partial refund",

    # ---- Account / Login ----
    "cannot login", "forgot password", "reset password",
    "account locked", "change email", "delete my account",

    # ---- Product / Pricing ----
    "product details", "price of this product",
    "is this product available", "out of stock",
    "discount available", "coupon not working",

    # ---- Escalation ----
    "talk to customer support", "connect me to an agent",
    "i need human support", "raise a ticket", "complaint",

    # ---- General FAQs ----
    "working hours", "customer care number",
    "how to contact support", "privacy policy"
]
