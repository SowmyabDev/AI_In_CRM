#!/usr/bin/env python
"""
Seed the database with sample data (users, orders, products).
"""

import sys
import os

# Add parent dir to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi_backend.database import init_db, UserDB, OrderDB, ProductDB


def seed_database():
    """
    Initialize and populate the database with sample products, users, and orders.
    """
    print("Initializing database schema...")
    init_db()
    
    print("Creating sample products...")
    products = [
        ("Wireless Earbuds X2", 1499, "Premium wireless earbuds with ANC and 30-hour battery life", 25, "Electronics"),
        ("Nike Running Shoes", 2999, "Lightweight running shoes with cushioned sole for comfort", 15, "Footwear"),
        ("USB-C Cable 2m", 299, "Fast charging USB-C cable, compatible with all devices", 50, "Accessories"),
        ("Smartphone Stand", 499, "Adjustable phone stand for desk and travel", 30, "Accessories"),
        ("Portable Power Bank", 1299, "20000mAh power bank with dual USB ports", 20, "Electronics"),
        ("Bluetooth Speaker", 1999, "Waterproof portable Bluetooth speaker with 360° sound", 18, "Electronics"),
    ]
    
    product_ids = {}
    for name, price, description, stock, category in products:
        pid = ProductDB.create_product(name, price, description, stock, category)
        product_ids[name] = pid
        print(f"  Created product: {name} (id={pid}, price=₹{price}, stock={stock})")
    
    print("\nCreating sample users...")
    users = [
        ("m25ai1060@iitj.ac.in", "12345", "Sowmya"),
        ("raj.patel@example.com", "password123", "Raj Patel"),
        ("priya.sharma@example.com", "secure_pass", "Priya Sharma"),
    ]
    
    user_ids = {}
    for email, password, name in users:
        uid = UserDB.create_user(email, password, name)
        if uid:
            user_ids[email] = uid
            print(f"  Created user: {name} ({email}, id={uid})")
        else:
            print(f"  User {email} already exists")
    
    print("\nCreating sample orders...")
    orders_data = [
        (users[0][0], "ORD001", "Delivered"),
        (users[0][0], "ORD002", "Out for Delivery"),
        (users[1][0], "ORD003", "Pending"),
        (users[1][0], "ORD004", "Delivered"),
        (users[2][0], "ORD005", "Processing"),
    ]
    
    for email, order_id, status in orders_data:
        uid = user_ids.get(email)
        if uid:
            success = OrderDB.create_order(uid, order_id, status)
            if success:
                print(f"  Created order: {order_id} (user={email}, status={status})")
            else:
                print(f"  Order {order_id} already exists")
    
    print("\n✅ Database seeded successfully!")
    print("\nSample user credentials:")
    for email, password, name in users:
        print(f"  Email: {email}")
        print(f"  Password: {password}")
        print(f"  Name: {name}")
        print()


if __name__ == "__main__":
    seed_database()
