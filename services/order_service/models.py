import datetime
import threading

# Simple thread-safe in-memory store for demo purposes
orders = {}
lock = threading.Lock()

def create_order(customer_id, products, pricing_result):
    """
    pricing_result: dict returned from Pricing Service containing total_amount and items
    """
    with lock:
        order_id = len(orders) + 1
        timestamp = datetime.datetime.utcnow().isoformat() + "Z"
        order = {
            "order_id": order_id,
            "customer_id": int(customer_id),
            "products": products,
            "pricing": pricing_result,
            "total_amount": pricing_result.get("total_amount", 0.0),
            "timestamp": timestamp,
            "status": "confirmed"
        }
        orders[order_id] = order
        return order

def get_order(order_id):
    return orders.get(int(order_id))

def get_all_orders():
    return list(orders.values())

def get_orders_by_customer(customer_id):
    return [o for o in orders.values() if o.get("customer_id") == int(customer_id)]



