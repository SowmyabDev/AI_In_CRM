import re
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles

from database import engine, SessionLocal
from models_db import Base, User, Session, Delivery
from schemas import LoginRequest, ChatRequest, ChatResponse
from intents import detect_intent
from crm_service import *
from llm_client import generate_llm_reply

Base.metadata.create_all(bind=engine)

app = FastAPI()
templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/", response_class=HTMLResponse)
def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})


@app.get("/chat_ui", response_class=HTMLResponse)
def chat_page(request: Request):
    return templates.TemplateResponse("chat.html", {"request": request})


@app.post("/login")
def login(req: LoginRequest):
    db = SessionLocal()
    user = db.query(User).filter_by(email=req.email).first()
    if not user or user.password != req.password:
        return {"success": False}

    db.merge(Session(session_id=req.session_id, user_id=user.id))
    db.commit()
    return {"success": True}


@app.post("/chat", response_model=ChatResponse)
def chat(req: ChatRequest):
    db = SessionLocal()

    session = db.query(Session).filter_by(
        session_id=req.session_id
    ).first()

    if not session:
        return ChatResponse(reply="Please log in first.")

    user_id = session.user_id

    # 🔍 ORDER-ID AWARE LOGIC (ORDYYYYMMDD)
    match = re.search(r"(ORD\d{8})", req.message.upper())
    if match:
        order_code = match.group(1)

        order = get_order_by_code(db, user_id, order_code)
        if not order:
            return ChatResponse(
                reply=f"❌ I couldn't find an order with ID {order_code}."
            )

        if "deliver" in req.message.lower() or "where" in req.message.lower():
            delivery = (
                db.query(Delivery)
                .filter(Delivery.order_id == order.id)
                .first()
            )
            if delivery:
                return ChatResponse(
                    reply=f"🚚 Order {order_code} is currently {delivery.status}."
                )
            else:
                return ChatResponse(
                    reply=f"📦 Order {order_code} is {order.status}."
                )

        return ChatResponse(
            reply=f"📦 Order {order_code} status: {order.status}."
        )

    # 🔍 INTENT-BASED FLOW
    intent = detect_intent(req.message)

    if intent == "greet":
        return ChatResponse(
            reply="Hello! 👋 How can I help you today?"
        )

    if intent == "goodbye":
        return ChatResponse(
        reply="😊 You’re welcome! Happy to help. If you need anything else, just let me know."
    )


    if intent == "my_orders":
        orders = get_orders(db, user_id)
        if not orders:
            return ChatResponse(reply="You have no orders.")

        return ChatResponse(
            reply="\n".join(
                f"{o.order_code} — {o.status}" for o in orders
            )
        )

    if intent == "delivery_status":
        deliveries = get_deliveries(db, user_id)
        if not deliveries:
            return ChatResponse(
                reply="You have no active deliveries."
            )

        return ChatResponse(
            reply="\n".join(
                f"🚚 {o} — {s}" for o, s in deliveries
            )
        )

    if intent == "show_cart":
        items = get_cart(db, user_id)
        return ChatResponse(
            reply=f"Your cart has {len(items)} item(s)."
        )

    if intent == "wishlist":
        try:
            items = get_wishlist(db, user_id)
            if not items:
                return ChatResponse(
                    reply="Your wishlist is empty."
                )

            names = "\n".join(f"• {row[0]}" for row in items)
            return ChatResponse(
                reply=f"🧡 Your wishlist:\n{names}"
            )
        except Exception:
            return ChatResponse(
                reply="⚠️ Unable to fetch wishlist right now."
            )

    if intent == "return_request":
        r = get_returns(db, user_id)
        return ChatResponse(
            reply="\n".join(
                f"{o} — {s}" for o, s in r
            ) or "No returns found."
        )

    if intent == "refund_query":
        r = get_refunds(db, user_id)
        return ChatResponse(
            reply="\n".join(
                f"{o} — ₹{a} ({s})" for o, a, s in r
            ) or "No refunds found."
        )
    
    if intent == "human_agent":
        return ChatResponse(
        reply="🔁 Redirecting you to a human agent. You’ll receive a callback shortly."
    )


    # 🔥 LLM FALLBACK
    # 🔥 LLM FALLBACK (general questions, policies, help, etc.)
    return ChatResponse(reply=generate_llm_reply(req.message))



@app.get("/health")
def health():
    return {"ok": True}
