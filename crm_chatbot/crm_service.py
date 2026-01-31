from models_db import (
    Order, CartItem, WishlistItem,
    Delivery, Return, Refund, Product
)

def get_orders(db, user_id):
    return db.query(Order).filter_by(user_id=user_id).all()

def get_cart(db, user_id):
    return (
        db.query(Product.name, CartItem.quantity)
        .join(Product, Product.id == CartItem.product_id)
        .filter(CartItem.user_id == user_id)
        .all()
    )

def get_wishlist(db, user_id):
    return (
        db.query(Product.name)
        .join(WishlistItem, Product.id == WishlistItem.product_id)
        .filter(WishlistItem.user_id == user_id)
        .all()
    )

def get_deliveries(db, user_id):
    return (
        db.query(Order.order_code, Delivery.status)
        .join(Delivery, Order.id == Delivery.order_id)
        .filter(
            Order.user_id == user_id,
            Delivery.status.in_([
                "Out for Delivery",
                "Preparing Shipment",
                "Shipped",
                "In Transit"
            ])
        )
        .all()
    )

def get_returns(db, user_id):
    return (
        db.query(Order.order_code, Return.status)
        .join(Return, Order.id == Return.order_id)
        .filter(Order.user_id == user_id)
        .all()
    )

def get_refunds(db, user_id):
    return (
        db.query(Order.order_code, Refund.amount, Refund.status)
        .join(Refund, Order.id == Refund.order_id)
        .filter(Order.user_id == user_id)
        .all()
    )

# 🔥 NEW: Fetch order by order_code
def get_order_by_code(db, user_id, order_code):
    return (
        db.query(Order)
        .filter(
            Order.user_id == user_id,
            Order.order_code == order_code
        )
        .first()
    )
