from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from intents import (
    detect_intent,
    extract_order_id,
    extract_product_id,
    search_products,
    product_details,
)
from llm_client import generate_reply, canned_reply
from carts import get_cart, add_to_cart, remove_from_cart
from users_db import USERS, ACTIVE_SESSIONS, ESCALATION_LOG

app = FastAPI(title="FastAPI")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

class ChatRequest(BaseModel):
    message: str
    session_id: str

class ChatResponse(BaseModel):
    reply: str

class LoginRequest(BaseModel):
    email: str
    password: str
    session_id: str


@app.get("/health")
def health():
    return {"ok": True}


@app.post("/login")
def login(req: LoginRequest):
    user = USERS.get(req.email)
    if not user or user["password"] != req.password:
        return {"success": False, "message": "Invalid username or password"}

    ACTIVE_SESSIONS[req.session_id] = req.email
    return {
        "success": True,
        "user": {
            "name": user["name"],
            "email": req.email,
            "phone": user["phone"],
            "orders": user.get("orders", []),
        },
    }


@app.post("/chat", response_model=ChatResponse)
def chat(req: ChatRequest):
    text = req.message.strip()
    session = req.session_id

    intent = detect_intent(text)
    order_id = extract_order_id(text)
    product_id = extract_product_id(text)

    if intent in ("order_status", "delivery_query"):
        if order_id:
            return ChatResponse(
                reply="I cannot view order details directly. I can connect you to a support agent. Would you like me to escalate this?"
            )
        return ChatResponse(
            reply="I cannot access order-specific delivery information. Please provide your order ID or reply 'connect me' for support."
        )

    if intent == "confirm_escalation":
        ESCALATION_LOG.append({"email": ACTIVE_SESSIONS.get(session), "issue": text})
        return ChatResponse(reply="Your request has been escalated to a human agent. You will receive a callback shortly.")

    if intent == "show_cart":
        cart = get_cart(session)
        if not cart:
            return ChatResponse(reply="Your cart is empty.")
        msg = "Your cart:\n" + "\n".join([f"- {c['name']} — ₹{c['price']}" for c in cart])
        return ChatResponse(reply=msg)

    if intent == "add_to_cart":
        if product_id:
            p = product_details(product_id)
            if p:
                add_to_cart(session, p)
                return ChatResponse(reply=f"Added {p['name']} to your cart.")
            return ChatResponse(reply="Invalid product ID.")
        return ChatResponse(reply="Please specify the product ID to add (e.g., 'add 101').")

    if intent == "remove_from_cart":
        if product_id:
            remove_from_cart(session, product_id)
            return ChatResponse(reply="Item removed from your cart.")
        return ChatResponse(reply="Please specify the product ID to remove (e.g., 'remove 101').")

    if intent == "my_orders":
        user_email = ACTIVE_SESSIONS.get(session)
        if not user_email:
            return ChatResponse(reply="Please log in first.")
        user = USERS.get(user_email)
        orders = user.get("orders", [])
        if not orders:
            return ChatResponse(reply="You have no orders.")
        msg = "Your orders:\n" + "\n".join([f"- {o['order_id']} — {o['status']}" for o in orders])
        return ChatResponse(reply=msg)

    if intent in ("return_request", "returns"):
        return ChatResponse(
            reply="Most items can be returned within 7 days of delivery. Please provide your order ID if you would like to start a return."
        )

    if intent in ("refund_query", "refund"):
        return ChatResponse(
            reply="Refunds are processed within 3–5 business days after the returned item is received. I cannot view order-specific refund details."
        )

    if intent in ("search", "product_info"):
        results = search_products(text)
        if not results:
            return ChatResponse(reply="No products found for that query.")
        msg = "Search results:\n" + "\n".join(
            [f"- #{p['id']} {p['name']} — ₹{p['price']}" for p in results[:5]]
        )
        return ChatResponse(reply=msg)

    if intent == "greet":
        return ChatResponse(reply="Hello. How can I assist you?")

    if intent == "ack":
        return ChatResponse(reply="😊 Sure! Let me know how else I can help.")

    if intent == "goodbye":
        return ChatResponse(reply="You're welcome. If you need further assistance, feel free to ask.")

    if intent == "human":
        ESCALATION_LOG.append({"email": ACTIVE_SESSIONS.get(session), "issue": text})
        return ChatResponse(reply="I will connect you to a human agent. You will receive a callback shortly.")

    reply = generate_reply(intent, text, {"user_email": ACTIVE_SESSIONS.get(session)})

    if not reply:
        ESCALATION_LOG.append({"email": ACTIVE_SESSIONS.get(session), "issue": text})
        return ChatResponse(reply="I’m unable to assist further. A human agent will follow up shortly.")

    return ChatResponse(reply=reply)
