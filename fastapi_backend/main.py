"""FastAPI Application for E-Commerce CRM Chatbot."""

from typing import Optional
from fastapi import FastAPI, HTTPException, status, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager

from fastapi_backend.config import settings
from fastapi_backend.logging_config import logger
from fastapi_backend.middleware import ErrorHandlingMiddleware, RequestLoggingMiddleware
from fastapi_backend.models import (
    ChatRequest, ChatResponse, LoginRequest, HealthResponse,
    ErrorResponse, AddToCartRequest, RemoveFromCartRequest
)
from fastapi_backend.intents import detect_intent
from fastapi_backend.llm_client import generate_llm_reply, classify_intent_with_llm
from fastapi_backend.users_db import ACTIVE_SESSIONS, authenticate_user, get_user_orders
from fastapi_backend.database import UserDB, CartDB, ProductDB
from fastapi_backend.carts import get_cart, add_to_cart, remove_from_cart
from fastapi_backend.analytics import analytics


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Application startup")
    yield
    logger.info("Application shutdown")


app = FastAPI(
    title=settings.API_TITLE,
    description=settings.API_DESCRIPTION,
    version=settings.API_VERSION,
    lifespan=lifespan
)

app.add_middleware(ErrorHandlingMiddleware)
app.add_middleware(RequestLoggingMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

logger.info(f"Application initialized")

def _get_email_for_session(session_id: str) -> Optional[str]:
    return ACTIVE_SESSIONS.get(session_id)


def _validate_session(session_id: str) -> str:
    email = _get_email_for_session(session_id)
    if not email:
        logger.warning(f"Invalid session: {session_id}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Session expired. Please login again."
        )
    return email


@app.get("/", tags=["Root"])
async def root():
    return {
        "message": settings.API_TITLE,
        "version": settings.API_VERSION,
        "docs": f"http://{settings.HOST}:{settings.PORT}/docs",
        "redoc": f"http://{settings.HOST}:{settings.PORT}/redoc",
    }


@app.get("/health", response_model=HealthResponse, tags=["Health"])
async def health():
    return HealthResponse(ok=True, version=settings.API_VERSION)


@app.post("/login", tags=["Auth"])
async def login(req: LoginRequest):
    if not authenticate_user(req.email, req.password):
        logger.warning(f"Failed login: {req.email}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )
    
    ACTIVE_SESSIONS[req.session_id] = req.email
    logger.info(f"User logged in: {req.email}")
    return {"success": True, "message": f"Welcome {req.email}"}


@app.post("/chat", response_model=ChatResponse, tags=["Chat"])
async def chat(req: ChatRequest):
    """
    Process user message: detect intent, route to chatbot or escalate to human.
    - Detect intent via regex or LLM
    - Escalate immediately if intent is not resolvable
    - Build context for LLM if resolvable
    - Record analytics for every interaction
    """
    try:
        text = (req.message or "").strip()
        session = req.session_id
        if not text:
            return ChatResponse(reply="Please provide a message.", intent="unknown")

        # Detect intent
        intent = detect_intent(text)
        if intent == "unknown":
            intent = classify_intent_with_llm(text)
        from fastapi_backend.intents import RESOLVABLE_INTENTS, ESCALATABLE_INTENTS
        is_resolvable = intent in RESOLVABLE_INTENTS
        is_escalatable = intent in ESCALATABLE_INTENTS
        logger.info(f"Intent: {intent} | Resolvable: {is_resolvable} | Escalatable: {is_escalatable} | Query: {text[:60]}")

        # Escalate if not resolvable
        if is_escalatable or not is_resolvable:
            analytics.record_query(intent, resolved=False)
            escalation_messages = {
                "return_request": "I understand you'd like to return your order. A specialist will help you with the return process.",
                "refund_query": "I'll connect you with our refund team to check your refund status.",
                "complaint": "I'm sorry to hear about your issue. Let me get a specialist to assist you.",
                "checkout": "For secure checkout, I'll connect you with our payment specialist.",
                "payment": "Let me connect you with our payment support team.",
                "account": "For account security, I'll have a specialist help you update your information.",
                "address": "For security, account changes should be handled by our team.",
                "wishlist": "Let me help you with your wishlist preferences.",
                "shipping": "I'll connect you with our shipping team for detailed assistance.",
                "human_handoff": "Connecting you with a human agent now."
            }
            reply = escalation_messages.get(intent, "I'm unable to resolve this. I'll connect you with a human agent for further assistance.")
            return ChatResponse(reply=reply, intent=intent)

        # Build context for LLM
        context = {
            "intent": intent,
            "user_text": text,
            "logged_in": session in ACTIVE_SESSIONS
        }
        email = _get_email_for_session(session)
        if email:
            context["user_email"] = email

        # Orders context
        if intent in ["my_orders", "order_status", "track_shipment"]:
            try:
                if email:
                    orders = get_user_orders(email)
                    context["user_orders"] = orders if orders else []
                else:
                    context["user_orders"] = []
            except Exception as e:
                logger.warning(f"Error fetching orders for {email}: {e}")
                context["user_orders"] = []

        # Cart context
        if intent in ["show_cart", "add_to_cart", "remove_from_cart", "clear_cart"]:
            try:
                cart = get_cart(session)
                context["cart_items"] = cart if cart else []
                if cart:
                    context["cart_total"] = sum(float(p.get('price', 0)) * int(p.get('quantity', 1)) for p in cart)
            except Exception as e:
                logger.warning(f"Error fetching cart: {e}")
                context["cart_items"] = []

        # Products context
        if intent in ["browse_products", "search_products", "product_details", "recommendations", "promotions"]:
            try:
                if intent == "search_products":
                    search_term = text.lower()
                    for prefix in ["search for", "find", "do you have", "look for", "show me"]:
                        search_term = search_term.replace(prefix, "").strip()
                    if search_term and len(search_term) >= 2:
                        products = ProductDB.search_products(search_term)
                        context["products"] = products[:10] if products else []
                    else:
                        context["products"] = []
                else:
                    all_products = ProductDB.get_all_products()
                    context["products"] = all_products[:10] if all_products else []
            except Exception as e:
                logger.warning(f"Error fetching products: {e}")
                context["products"] = []

        # Generate reply using LLM
        reply = generate_llm_reply(text, context)
        analytics.record_query(intent, resolved=True)
        return ChatResponse(reply=reply, intent=intent)

    except Exception as e:
        logger.error(f"Chat endpoint error: {str(e)}", exc_info=True)
        analytics.record_query("unknown", resolved=False)
        return ChatResponse(reply="I encountered an error processing your request. Please try again.", intent="unknown")


@app.get("/products", tags=["Products"])
async def get_products():
    try:
        products = ProductDB.get_all_products()
        logger.info(f"Retrieved {len(products)} products")
        return {"products": products, "count": len(products)}
    except Exception as e:
        logger.error(f"Error fetching products: {str(e)}")
        raise HTTPException(status_code=500, detail="Error fetching products")


@app.get("/products/search", tags=["Products"])
async def search_products(query: str = ""):
    try:
        if not query or len(query) < 2:
            raise HTTPException(status_code=400, detail="Query must be at least 2 characters")
        
        products = ProductDB.search_products(query)
        logger.info(f"Search for '{query}' returned {len(products)} results")
        return {"products": products, "count": len(products), "query": query}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Search error: {str(e)}")
        raise HTTPException(status_code=500, detail="Search failed")


@app.get("/products/{product_id}", tags=["Products"])
async def get_product_details(product_id: int):
    try:
        product = ProductDB.get_product_by_id(product_id)
        if not product:
            raise HTTPException(status_code=404, detail="Product not found")
        return product
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching product {product_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Error fetching product")


@app.post("/cart/add", tags=["Cart"])
async def add_item_to_cart(req: AddToCartRequest):
    try:
        success, message = add_to_cart(req.session_id, req.product_id, req.quantity)
        if not success:
            logger.warning(f"Failed to add to cart: {message}")
            raise HTTPException(status_code=400, detail=message)
        logger.info(f"Item {req.product_id} added to cart")
        return {"success": True, "message": message}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Cart add error: {str(e)}")
        raise HTTPException(status_code=500, detail="Error adding to cart")


@app.post("/cart/remove", tags=["Cart"])
async def remove_item_from_cart(req: RemoveFromCartRequest):
    try:
        success, message = remove_from_cart(req.session_id, req.product_id)
        if not success:
            logger.warning(f"Failed to remove from cart: {message}")
            raise HTTPException(status_code=400, detail=message)
        logger.info(f"Item {req.product_id} removed from cart")
        return {"success": True, "message": message}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Cart remove error: {str(e)}")
        raise HTTPException(status_code=500, detail="Error removing from cart")


@app.get("/analytics/metrics", tags=["Analytics"])
async def get_analytics():
    try:
        metrics = analytics.get_metrics_summary()
        logger.info(f"Analytics retrieved: {metrics['total_queries']} total queries")
        return metrics
    except Exception as e:
        logger.error(f"Analytics error: {str(e)}")
        raise HTTPException(status_code=500, detail="Error retrieving analytics")


@app.get("/analytics/staffing", tags=["Analytics"])
async def staffing_analysis():
    try:
        from fastapi_backend.simulation import run_staffing_analysis
        
        escalation_rate = analytics.get_escalation_rate()
        escalated_per_hour = settings.QUERIES_PER_HOUR_BASELINE * escalation_rate
        
        logger.info(f"Running staffing analysis | Escalation rate: {escalation_rate*100:.1f}%")
        results = run_staffing_analysis(escalated_per_hour, num_simulations=2)
        
        return {
            "chatbot_resolution_rate": analytics.get_resolution_rate(),
            "escalation_rate": escalation_rate,
            "estimated_escalations_per_hour": escalated_per_hour,
            "staffing_scenarios": results
        }
    except Exception as e:
        logger.error(f"Staffing analysis error: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Error running staffing analysis")


@app.exception_handler(ValueError)
async def value_error_handler(request: Request, exc: ValueError):
    logger.error(f"Validation error: {str(exc)}")
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={"error": "Validation Error", "details": str(exc)}
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app,
        host=settings.HOST,
        port=settings.PORT,
        log_level=settings.LOG_LEVEL.lower()
    )
