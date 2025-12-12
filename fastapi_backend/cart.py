USER_CARTS = {}

def get_cart(session_id):
    return USER_CARTS.get(session_id, [])

def add_to_cart(session_id, product):
    USER_CARTS.setdefault(session_id, []).append(product)

def remove_from_cart(session_id, pid):
    USER_CARTS[session_id] = [
        p for p in USER_CARTS.get(session_id, []) if p["id"] != pid
    ]
