import os
import logging
from typing import Dict
import requests

# Configure logger
LOGGER = logging.getLogger("llm_client")
logging.basicConfig(level=logging.INFO)

# Environment/configuration
OLLAMA_BASE_URL = os.environ.get("OLLAMA_URL", "http://localhost:11434")
OLLAMA_URL = OLLAMA_BASE_URL + "/api/generate"
MODEL = os.environ.get("LLM_MODEL", "phi3:mini")  # Default to phi3:mini if available
TEMPERATURE = float(os.environ.get("LLM_TEMPERATURE", "0.7"))
TIMEOUT = int(os.environ.get("LLM_TIMEOUT", "120000"))  # Increased to 120s for larger models like Mistral

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

SYSTEM_PROMPT = """Follow these rules strictly:
Respond clearly and concisely (max 3 sentences unless required).
Use only information provided in the Context—never guess or invent.
If information is unavailable, say: “I don’t have that information. Would you like me to connect to the human agent?”
Require users to log in for any personal, order, or account data.
Always be factual and accurate.

Handle user intents as follows:
6. Orders: Confirm ID, status, and items from Context only.
7. Products: List matches from Context only.
8. Cart: Show items and totals; encourage checkout when appropriate.
9. Account: Direct users to log in or use secure account settings.
10. General: Provide platform help without speculation.

If a request cannot be fulfilled:
11. Missing data → Ask user to log in.
12. No results → Ask user to refine the request.
13. Unsupported → State limitation and suggest contacting support.

Tone:
14. Professional, friendly, and natural—no filler or assumptions."""

def get_available_models() -> list:
    """Fetch list of available models from Ollama."""
    try:
        resp = requests.get(f"{OLLAMA_BASE_URL}/api/tags", timeout=5)
        if resp.status_code == 200:
            models = resp.json().get("models", [])
            return [m.get("name") for m in models if m.get("name")]
    except Exception as e:
        LOGGER.warning(f"Failed to fetch available models: {e}")
    return []

def get_best_available_model() -> str:
    """Get the best available model from Ollama, fallback if needed."""
    available = get_available_models()
    if not available:
        LOGGER.warning("No models available from Ollama")
        return MODEL  # Return default
    
    # Prefer mistral, then phi3:mini, then any available
    # for preferred in ["mistral:latest", "mistral", "phi3:mini", "phi3"]:
    for preferred in ["phi3:mini", "phi3"]:
        for model in available:
            if preferred in model.lower() or model.lower() in preferred:
                LOGGER.info(f"Selected model: {model}")
                return model
    
    # If no preferred model, return the first available
    selected = available[0]
    LOGGER.info(f"No preferred model found, using: {selected}")
    return selected

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
        model_name = get_best_available_model()
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
    try:
        # Format context nicely
        context_str = "\n".join([f"- {k}: {v}" for k, v in context.items()])
        prompt = f"""{SYSTEM_PROMPT}

Context:
{context_str}

User: {user_text}
"""
        model_name = get_best_available_model()
        payload = {
            "model": model_name,
            "prompt": prompt,
            "stream": False,
            "temperature": TEMPERATURE
        }
        LOGGER.info(f"Sending request to Ollama with model: {model_name}")
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
    except Exception as e:
        LOGGER.exception(f"Unexpected error in generate_llm_reply: {e}")
        return "I encountered an unexpected error. Please try again."