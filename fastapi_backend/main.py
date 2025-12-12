# main.py
from users_db import USERS, ESCALATION_LOG

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from models import ChatRequest, ChatResponse
from intents import detect_intent, search_products, product_details, FAQ
from cart import get_cart, add_to_cart, remove_from_cart
from llm_client import generate_llm_reply
import re

app = FastAPI(title="E-commerce Hybrid Chatbot (safe)")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

CANNOT_ACCESS_MSG = (
    "I’m sorry — I can’t access your account or order data from here. "
    "If you share your order ID I can guide you on next steps, or I can connect you to a human agent. "
    "Reply 'connect me' to escalate."
)

ESCALATION_INSTRUCTIONS = (
    "To contact human support: call +1-800-XXX-XXXX or reply 'connect me' and include your order ID."
)

def sanitize_llm_output(text: str) -> str:
    if not text:
        return None
    lowered = text.lower()
    forbidden_phrases = ["i checked", "i have checked", "i see your order", "i found your order", "i can access", "i looked up"]
    if any(phr in lowered for phr in forbidden_phrases):
        return CANNOT_ACCESS_MSG
    return text.strip()

@app.post("/chat", response_model=ChatResponse)
def chat(req: ChatRequest):
    text = req.message.strip()
    session = req.session_id
    intent = detect_intent(text)

    if intent == "greet":
        return ChatResponse(reply="Hi! 👋 How can I help you today?")

    if intent == "show_cart":
        items = get_cart(session)
        if not items:
            return ChatResponse(reply="Your cart is currently empty.")
        msg = "Your cart contains:\n" + "\n".join([f"- {i['name']} — ₹{i['price']}" for i in items])
        return ChatResponse(reply=msg)

    if intent == "add_to_cart":
        m = re.search(r"\b(\d{2,6})\b", text)
        if m:
            pid = int(m.group(1))
            p = product_details(pid)
            if p:
                add_to_cart(session, p)
                return ChatResponse(reply=f"Added **{p['name']}** to your cart.")
            return ChatResponse(reply="I couldn't find that product ID. Please check the ID and try again.")
        return ChatResponse(reply="Please tell me which product ID to add (e.g., 'add 101').")

    if intent == "remove_from_cart":
        m = re.search(r"\b(\d{2,6})\b", text)
        if m:
            pid = int(m.group(1))
            remove_from_cart(session, pid)
            return ChatResponse(reply="Item removed from your cart.")
        return ChatResponse(reply="Please specify the product id to remove (e.g., 'remove 101').")

    if intent == "product_info":
        m = re.search(r"\b(\d{2,6})\b", text)
        if m:
            pid = int(m.group(1))
            p = product_details(pid)
            if p:
                return ChatResponse(reply=f"{p['name']} — ₹{p['price']}\nCategory: {p['category']}")
        return ChatResponse(reply="Please provide a valid product id (e.g., 'product 101').")

    if intent == "search":
        q = re.sub(r"\b(search|find|look for)\b", "", text, flags=re.I).strip()
        results = search_products(q)
        if not results:
            return ChatResponse(reply=f"No products found for '{q}'. Try a different keyword.")
        msg = "Search results:\n" + "\n".join([f"- #{p['id']} {p['name']} — ₹{p['price']}" for p in results])
        msg += "\nTo add to cart: 'add <id>'"
        return ChatResponse(reply=msg)
    
    if intent in ("returns", "refund", "delivery"):
        base = FAQ.get(intent, "Sorry, I don't have that information right now.")
        llm = generate_llm_reply(text)
        if llm:
            safe = sanitize_llm_output(llm)
            if safe == CANNOT_ACCESS_MSG:
                return ChatResponse(reply=f"{base} {ESCALATION_INSTRUCTIONS}")
            return ChatResponse(reply=safe)
        return ChatResponse(reply=f"{base} {ESCALATION_INSTRUCTIONS}")

    if intent in ("order_status", "cancel", "human"):
        if "connect" in text.lower() or "connect me" in text.lower() or intent == "human":
            return ChatResponse(reply=ESCALATION_INSTRUCTIONS)
        m = re.search(r"\b([A-Z0-9]{5,20})\b", text, flags=re.I)
        if not m:
            return ChatResponse(reply="I can't access your order details here. Please provide your order ID (or reply 'connect me' to reach human support).")
        return ChatResponse(reply="Thanks — I have your order ID. I can't view it here. Reply 'connect me' to escalate this to a human agent who can access your order and help further.")

    if intent == "human" or "connect me" in text.lower():
        ESCALATION_LOG.append({
            "email": "UNKNOWN USER",  
            "issue": text
        })

        return ChatResponse(reply=(
            "Your issue has been escalated to a human support agent. "
            "You will receive a callback shortly. 📞"
        ))


    llm_ans = generate_llm_reply(text)
    if llm_ans:
        safe = sanitize_llm_output(llm_ans)
        if safe == CANNOT_ACCESS_MSG:
            return ChatResponse(reply=f"{CANNOT_ACCESS_MSG}\n{ESCALATION_INSTRUCTIONS}")
        return ChatResponse(reply=safe)

    return ChatResponse(reply=(
        "Sorry, I couldn't understand that. I can help with orders, returns, refunds, delivery, search and cart actions. "
        "If you need human support, reply 'connect me'."
    ))


@app.post("/login")
def login(data: dict):
    email = data.get("email")
    password = data.get("password")

    user = USERS.get(email)
    if not user or user["password"] != password:
        return {"success": False, "message": "Invalid email or password"}

    return {
        "success": True,
        "message": "Login successful",
        "user": {
            "name": user["name"],
            "email": email,
            "phone": user["phone"],
            "orders": user["orders"]
        }
    }


@app.post("/escalate")
def escalate(data: dict):
    email = data.get("email")
    issue = data.get("issue")

    ESCALATION_LOG.append({
        "email": email,
        "issue": issue
    })

    return {
        "success": True,
        "message": "Your issue has been escalated to a human agent. You will receive a callback shortly."
    }
 