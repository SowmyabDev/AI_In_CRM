import os
import logging
from typing import Dict
import requests

# Configure logger
LOGGER = logging.getLogger("llm_client")
logging.basicConfig(level=logging.INFO)

# Environment/configuration
OLLAMA_URL = os.environ.get("OLLAMA_URL", "http://localhost:11434/api/generate")
MODEL = os.environ.get("LLM_MODEL", "mistral")
TEMPERATURE = float(os.environ.get("LLM_TEMPERATURE", "0.7"))
TIMEOUT = int(os.environ.get("LLM_TIMEOUT", "30"))

# Supported model configurations
MODEL_CONFIG = {
    "mistral": {
        "name": "mistral:latest",
        "description": "Mistral 7B - Best quality, excellent instruction-following",
        "context_length": 8192,
        "recommended": True
    },
    "phi3:mini": {
        "name": "phi3:mini",
        "description": "Phi-3 Mini - Lightweight, fast, good for edge devices",
        "context_length": 4096,
        "recommended": False
    },
    "neural-chat": {
        "name": "neural-chat:latest",
        "description": "Neural Chat 7B - Optimized for conversation",
        "context_length": 4096,
        "recommended": False
    },
    "llama2": {
        "name": "llama2:latest",
        "description": "Llama 2 7B - Good quality, widely tested",
        "context_length": 4096,
        "recommended": False
    }
}

SYSTEM_PROMPT = """You are a friendly and professional customer support assistant for an e-commerce platform. Your role is to help customers with inquiries about their orders, products, and account.

CORE RULES:
1. Be helpful, friendly, and concise. Keep responses under 3 sentences unless more detail is needed.
2. Use only information provided in the Context. Never invent order details, prices, or product information.
3. If asked about data not in Context, say "I don't have that information" rather than guessing.
4. For logged-out users asking for personal data: suggest they log in first.
5. Always be factual about product details, order status, and policies.

HANDLING DIFFERENT INTENTS:
- Order queries: Use Context data (order IDs, statuses, items). Confirm order details found.
- Product search: List matching products with available information from Context.
- Cart management: Show items and totals, encourage checkout when appropriate.
- General questions: Provide helpful, accurate information about the platform.
- Account/Profile: Politely ask users to log in or update profile through secure channels.

IF USER DATA IS NOT AVAILABLE:
- "I don't have your order history. Could you log in to check your orders?"
- "I can't find products matching that search. Could you try different keywords?"
- "That information isn't available to me. Please contact support for assistance."

TONE: Professional but warm. Use natural language, avoid robotic responses. Be adaptable to any e-commerce platform style."""

def classify_intent_with_llm(user_text: str) -> str:
    """
    Use LLM to classify user intent when regex fails.
    Returns a valid intent string or 'unknown'.
    """
    intent_prompt = f"""Classify the user's message into ONE of these intent categories:
greet, goodbye, ack, my_orders, order_status, show_cart, add_to_cart, remove_from_cart, 
browse_products, search_products, product_details, checkout, shipping, payment, account, 
address, recommendations, promotions, track_shipment, clear_cart, wishlist, human_handoff

User message: "{user_text}"

Respond with ONLY the intent name, nothing else."""
    try:
        model_name = MODEL_CONFIG.get(MODEL, {}).get("name", MODEL)
        payload = {
            "model": model_name,
            "prompt": intent_prompt,
            "stream": False,
            "temperature": TEMPERATURE
        }
        response = requests.post(OLLAMA_URL, json=payload, timeout=TIMEOUT)
        response.raise_for_status()
        result = response.json()
        classified_intent = result.get("response", "").strip().lower()
        valid_intents = [
            "greet", "goodbye", "ack", "my_orders", "order_status", "show_cart",
            "add_to_cart", "remove_from_cart", "browse_products", "search_products",
            "product_details", "checkout", "shipping", "payment", "account",
            "address", "recommendations", "promotions", "track_shipment",
            "clear_cart", "wishlist", "human_handoff"
        ]
        if classified_intent in valid_intents:
            LOGGER.info(f"LLM classified '{user_text}' as '{classified_intent}'")
            return classified_intent
        LOGGER.warning(f"LLM returned unknown intent: '{classified_intent}' for input: {user_text}")
        return "unknown"
    except Exception as e:
        LOGGER.warning(f"Intent classification failed: {e}")
        return "unknown"

def generate_llm_reply(user_text: str, context: Dict) -> str:
    """
    Generate a response using the LLM (Ollama).
    Returns a string reply. Handles all error cases gracefully.
    """
    prompt = f"""{SYSTEM_PROMPT}

Context:
{context}

User:
{user_text}
"""
    model_name = MODEL_CONFIG.get(MODEL, {}).get("name", MODEL)
    payload = {
        "model": model_name,
        "prompt": prompt,
        "stream": False,
        "temperature": TEMPERATURE
    }
    try:
        resp = requests.post(OLLAMA_URL, json=payload, timeout=TIMEOUT)
        resp.raise_for_status()
        data = resp.json()
        text = data.get("response") or data.get("text") or data.get("output")
        if not text:
            LOGGER.warning(f"LLM returned unexpected payload: {data}")
            return "I'm here to help. Could you please rephrase your question?"
        return str(text).strip()
    except requests.Timeout:
        LOGGER.error(f"LLM request timeout ({TIMEOUT}s). Model may be overloaded.")
        return "I'm taking a bit longer to process. Please try again in a moment."
    except requests.ConnectionError:
        LOGGER.error(f"Failed to connect to LLM at {OLLAMA_URL}. Is Ollama running?")
        return "I'm temporarily unavailable. Please try again shortly."
    except requests.RequestException as e:
        LOGGER.exception(f"LLM request failed: {e}")
        return "I encountered an error. Could you please try again?"