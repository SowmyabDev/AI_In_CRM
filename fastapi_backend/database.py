"""SQLite database setup and models for CRM chatbot."""

import sqlite3
import os
from typing import Optional, List, Dict, Any
from contextlib import contextmanager
import hashlib

DB_PATH = os.environ.get("DB_PATH", "crm_chatbot.db")


def init_db() -> None:
    """Initialize the database schema."""
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        
        # Users table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            name TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """)
        
        # Orders table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            order_id TEXT UNIQUE NOT NULL,
            status TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
        """)
        
        # Products table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            price REAL NOT NULL,
            description TEXT,
            stock INTEGER DEFAULT 0,
            category TEXT,
            rating REAL DEFAULT 0.0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """)
        
        # Cart items table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS cart_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id TEXT NOT NULL,
            product_id INTEGER NOT NULL,
            quantity INTEGER DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (product_id) REFERENCES products (id)
        )
        """)
        
        # User addresses table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS addresses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            type TEXT DEFAULT 'shipping',
            street TEXT NOT NULL,
            city TEXT NOT NULL,
            state TEXT NOT NULL,
            zip_code TEXT NOT NULL,
            is_default BOOLEAN DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
        """)
        
        # Reviews table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS reviews (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            product_id INTEGER NOT NULL,
            user_id INTEGER NOT NULL,
            rating INTEGER NOT NULL,
            comment TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (product_id) REFERENCES products (id),
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
        """)
        
        conn.commit()


def hash_password(password: str) -> str:
    """Hash a password using SHA256."""
    return hashlib.sha256(password.encode()).hexdigest()


@contextmanager
def get_db_connection():
    """Context manager for database connections."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()


class UserDB:
    """User database operations."""
    
    @staticmethod
    def create_user(email: str, password: str, name: str) -> Optional[int]:
        """Create a new user. Returns user id on success, None if email exists."""
        try:
            with get_db_connection() as conn:
                cursor = conn.cursor()
                password_hash = hash_password(password)
                cursor.execute(
                    "INSERT INTO users (email, password_hash, name) VALUES (?, ?, ?)",
                    (email, password_hash, name)
                )
                conn.commit()
                return cursor.lastrowid
        except sqlite3.IntegrityError:
            return None
    
    @staticmethod
    def get_user_by_email(email: str) -> Optional[Dict[str, Any]]:
        """Get user by email."""
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id, email, name FROM users WHERE email = ?", (email,))
            row = cursor.fetchone()
            if row:
                return dict(row)
            return None
    
    @staticmethod
    def authenticate(email: str, password: str) -> bool:
        """Authenticate user with email and password."""
        with get_db_connection() as conn:
            cursor = conn.cursor()
            password_hash = hash_password(password)
            cursor.execute(
                "SELECT id FROM users WHERE email = ? AND password_hash = ?",
                (email, password_hash)
            )
            return cursor.fetchone() is not None


class OrderDB:
    """Order database operations."""
    
    @staticmethod
    def create_order(user_id: int, order_id: str, status: str = "Pending") -> bool:
        """Create a new order."""
        try:
            with get_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "INSERT INTO orders (user_id, order_id, status) VALUES (?, ?, ?)",
                    (user_id, order_id, status)
                )
                conn.commit()
                return True
        except sqlite3.IntegrityError:
            return False
    
    @staticmethod
    def get_user_orders(user_id: int) -> List[Dict[str, Any]]:
        """Get all orders for a user."""
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT order_id, status FROM orders WHERE user_id = ? ORDER BY created_at DESC",
                (user_id,)
            )
            return [dict(row) for row in cursor.fetchall()]


class ProductDB:
    """Product database operations."""
    
    @staticmethod
    def create_product(name: str, price: float, description: str = "", stock: int = 0, category: str = "") -> int:
        """Create a new product. Returns product id."""
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO products (name, price, description, stock, category) VALUES (?, ?, ?, ?, ?)",
                (name, price, description, stock, category)
            )
            conn.commit()
            return cursor.lastrowid
    
    @staticmethod
    def get_all_products() -> List[Dict[str, Any]]:
        """Get all products."""
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id, name, price, description, stock, category, rating FROM products ORDER BY name")
            return [dict(row) for row in cursor.fetchall()]
    
    @staticmethod
    def search_products(query: str) -> List[Dict[str, Any]]:
        """Search products by name or description."""
        with get_db_connection() as conn:
            cursor = conn.cursor()
            search_term = f"%{query}%"
            cursor.execute(
                "SELECT id, name, price, description, stock, category, rating FROM products WHERE name LIKE ? OR description LIKE ? ORDER BY name",
                (search_term, search_term)
            )
            return [dict(row) for row in cursor.fetchall()]
    
    @staticmethod
    def get_products_by_category(category: str) -> List[Dict[str, Any]]:
        """Get products by category."""
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT id, name, price, description, stock, category, rating FROM products WHERE category = ? ORDER BY name",
                (category,)
            )
            return [dict(row) for row in cursor.fetchall()]
    
    @staticmethod
    def get_top_rated_products(limit: int = 5) -> List[Dict[str, Any]]:
        """Get top-rated products."""
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT id, name, price, description, stock, category, rating FROM products WHERE rating > 0 ORDER BY rating DESC LIMIT ?",
                (limit,)
            )
            return [dict(row) for row in cursor.fetchall()]
    
    @staticmethod
    def get_product_by_id(product_id: int) -> Optional[Dict[str, Any]]:
        """Get product by id."""
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id, name, price, description, stock, category, rating FROM products WHERE id = ?", (product_id,))
            row = cursor.fetchone()
            if row:
                return dict(row)
            return None
    
    @staticmethod
    def check_stock(product_id: int) -> int:
        """Check product stock availability."""
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT stock FROM products WHERE id = ?", (product_id,))
            row = cursor.fetchone()
            return row[0] if row else 0


class CartDB:
    """Cart database operations."""
    
    @staticmethod
    def add_to_cart(session_id: str, product_id: int, quantity: int = 1) -> bool:
        """Add item to cart."""
        try:
            with get_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "INSERT INTO cart_items (session_id, product_id, quantity) VALUES (?, ?, ?)",
                    (session_id, product_id, quantity)
                )
                conn.commit()
                return True
        except sqlite3.IntegrityError:
            return False
    
    @staticmethod
    def get_cart(session_id: str) -> List[Dict[str, Any]]:
        """Get all items in cart for a session."""
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT p.id, p.name, p.price, c.quantity
                FROM cart_items c
                JOIN products p ON c.product_id = p.id
                WHERE c.session_id = ?
                """,
                (session_id,)
            )
            return [dict(row) for row in cursor.fetchall()]
    
    @staticmethod
    def remove_from_cart(session_id: str, product_id: int) -> bool:
        """Remove item from cart."""
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "DELETE FROM cart_items WHERE session_id = ? AND product_id = ?",
                (session_id, product_id)
            )
            conn.commit()
            return cursor.rowcount > 0
    
    @staticmethod
    def clear_cart(session_id: str) -> None:
        """Clear all items from cart."""
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM cart_items WHERE session_id = ?", (session_id,))
            conn.commit()
