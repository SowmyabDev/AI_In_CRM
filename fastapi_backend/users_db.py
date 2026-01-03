"""User database layer. Uses SQLite backend for persistence.

This module provides a compatibility layer for auth and session management.
"""

from fastapi_backend.database import UserDB, OrderDB, init_db

# Initialize database on module import
init_db()

# In-memory session management (can be moved to DB for production)
ACTIVE_SESSIONS = {}
TICKETS = []


def authenticate_user(email: str, password: str) -> bool:
    """Return True if the user exists and password matches.
    
    Passwords are hashed with SHA256 in the database.
    """
    return UserDB.authenticate(email, password)


def get_user_orders(email: str):
    """Get orders for a user by email.
    
    Returns a list of order dicts or empty list if user not found.
    """
    user = UserDB.get_user_by_email(email)
    if not user:
        return []
    return OrderDB.get_user_orders(user["id"])
