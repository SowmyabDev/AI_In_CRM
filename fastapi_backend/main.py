from fastapi import FastAPI
from models import ChatRequest, ChatResponse, LoginRequest
from intents import detect_intent
from llm_client import generate_llm_reply
from users_db import USERS, ACTIVE_SESSIONS
from carts import get_cart

app = FastAPI()


@app.post("/login")
def login(req: LoginRequest):
    user = USERS.get(req.email)
    if not user or user["password"] != req.password:
        return {"success": False, "message": "Invalid credentials"}

    ACTIVE_SESSIONS[req.session_id] = req.email
    return {"success": True}


@app.post("/chat", response_model=ChatResponse)
def chat(req: ChatRequest):
    text = req.message.strip()
    session = req.session_id
    intent = detect_intent(text)

    if intent == "greet":
        return ChatResponse(reply="Hello! How can I help you today?")

    if intent == "goodbye":
        return ChatResponse(reply="You’re welcome. Have a great day!")

    if intent == "ack":
        return ChatResponse(reply="Sure. Let me know how else I can help.")

    if intent == "my_orders":
        email = ACTIVE_SESSIONS.get(session)
        if not email:
            return ChatResponse(reply="Please log in to view your orders.")

        orders = USERS[email].get("orders", [])
        if not orders:
            return ChatResponse(reply="You have no orders.")

        msg = "Your orders:\n" + "\n".join(
            [f"- {o['order_id']} — {o['status']}" for o in orders]
        )
        return ChatResponse(reply=msg)

    if intent == "show_cart":
        cart = get_cart(session)
        if not cart:
            return ChatResponse(reply="Your cart is empty.")
        msg = "Your cart:\n" + "\n".join(
            [f"- {p['name']} — ₹{p['price']}" for p in cart]
        )
        return ChatResponse(reply=msg)
    
    if intent == "human_handoff":
        return ChatResponse(
            reply="Your request has been escalated to a human agent. You will receive a callback shortly."
        )


    context = {
        "intent": intent,
        "logged_in": session in ACTIVE_SESSIONS
    }

    reply = generate_llm_reply(text, context)
    return ChatResponse(reply=reply)
