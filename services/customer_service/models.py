from database import create_connection
import requests
import os

ORDER_SERVICE_BY_CUSTOMER = "http://localhost:5001/api/orders/customer"
ORDER_SERVICE_ALL = "http://localhost:5001/api/orders"
HTTP_TIMEOUT = 5

def get_customer(customer_id):
    conn = create_connection()
    if not conn:
        return None
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT customer_id, name, email, phone, loyalty_points, created_at FROM customers WHERE customer_id=%s", (customer_id,))
    customer = cursor.fetchone()
    conn.close()
    return customer

def update_loyalty_points(customer_id, points):
    conn = create_connection()
    if not conn:
        return False
    cursor = conn.cursor()
    cursor.execute("UPDATE customers SET loyalty_points = loyalty_points + %s WHERE customer_id = %s", (points, customer_id))
    conn.commit()
    conn.close()
    return True

def get_customer_orders(customer_id):
    # First try dedicated endpoint
    try:
        resp = requests.get(f"{ORDER_SERVICE_BY_CUSTOMER}/{customer_id}", timeout=HTTP_TIMEOUT)
        if resp.status_code == 200:
            return resp.json()
    except requests.RequestException:
        pass

    # Fallback: query all orders and filter
    try:
        resp = requests.get(ORDER_SERVICE_ALL, timeout=HTTP_TIMEOUT)
        if resp.status_code == 200:
            orders = resp.json()
            return [o for o in orders if o.get("customer_id") == int(customer_id)]
    except requests.RequestException:
        pass

    return []
