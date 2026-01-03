"""
Cart management utilities for session-based carts.
"""

from typing import Any, Dict, List

# In-memory user cart storage (session_id -> list of product dicts)
USER_CARTS: Dict[str, List[Dict[str, Any]]] = {}


def get_cart(session_id: str) -> List[Dict[str, Any]]:
    """Return the cart for a given session_id."""
    return USER_CARTS.get(session_id, [])


def add_to_cart(session_id: str, product: Dict[str, Any]) -> None:
    """Add a product to the user's cart."""
    USER_CARTS.setdefault(session_id, []).append(product)


def remove_from_cart(session_id: str, pid: int) -> None:
    """Remove a product from the user's cart by product id."""
    if session_id not in USER_CARTS:
        return
    USER_CARTS[session_id] = [p for p in USER_CARTS.get(session_id, []) if p.get("id") != pid]
