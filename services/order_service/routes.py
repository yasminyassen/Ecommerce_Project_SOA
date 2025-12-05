from flask import Flask, request, jsonify
import requests
from models import create_order, get_order, get_all_orders, get_orders_by_customer

app = Flask(__name__)

INVENTORY_SERVICE_URL = "http://localhost:5002/api/inventory"
CUSTOMER_SERVICE_URL = "http://localhost:5004/api/customers"
PRICING_SERVICE_URL = "http://localhost:5003/api/pricing/calculate"

# Timeout for inter-service HTTP calls (seconds)
HTTP_TIMEOUT = 5

@app.route("/api/orders/create", methods=["POST"])
def create_order_endpoint():
    data = request.get_json()
    if not data:
        return jsonify({"error": "Invalid JSON"}), 400

    customer_id = data.get("customer_id")
    products = data.get("products")
    region = data.get("region")  # optional, forwarded to pricing
    if not customer_id or not isinstance(products, list) or len(products) == 0:
        return jsonify({"error": "Missing customer_id or products list"}), 400

    # Validate customer exists
    try:
        resp = requests.get(f"{CUSTOMER_SERVICE_URL}/{customer_id}", timeout=HTTP_TIMEOUT)
    except requests.RequestException:
        return jsonify({"error": "Customer service unreachable"}), 502

    if resp.status_code != 200:
        return jsonify({"error": f"Customer {customer_id} not found"}), 404

    # Validate inventory availability before pricing/creating order
    for item in products:
        product_id = item.get("product_id")
        qty = int(item.get("quantity", 0))
        if not product_id or qty <= 0:
            return jsonify({"error": "Invalid product data"}), 400

        try:
            inv_resp = requests.get(f"{INVENTORY_SERVICE_URL}/check/{product_id}", timeout=HTTP_TIMEOUT)
        except requests.RequestException:
            return jsonify({"error": "Inventory service unreachable"}), 502

        if inv_resp.status_code != 200:
            return jsonify({"error": f"Product {product_id} not found in inventory"}), 404

        stock = inv_resp.json()
        if stock.get("quantity_available", 0) < qty:
            return jsonify({"error": f"Not enough stock for product {product_id}"}), 400

    # Call Pricing Service to calculate totals (authoritative)
    pricing_payload = {"products": products}
    if region:
        pricing_payload["region"] = region

    try:
        price_resp = requests.post(PRICING_SERVICE_URL, json=pricing_payload, timeout=HTTP_TIMEOUT)
    except requests.RequestException:
        return jsonify({"error": "Pricing service unreachable"}), 502

    if price_resp.status_code != 200:
        # forward error message from pricing if available
        try:
            return jsonify(price_resp.json()), price_resp.status_code
        except Exception:
            return jsonify({"error": "Pricing service error"}), 502

    pricing_result = price_resp.json()

    # After pricing OK, update inventory (decrement)
    for item in products:
        product_id = item["product_id"]
        qty = int(item["quantity"])
        try:
            upd_resp = requests.put(
                f"{INVENTORY_SERVICE_URL}/update",
                json={"product_id": product_id, "quantity_sold": qty},
                timeout=HTTP_TIMEOUT
            )
        except requests.RequestException:
            # NOTE: In production you'd implement compensation (saga) here.
            return jsonify({"error": "Failed to update inventory (inventory service unreachable)"}), 502

        if upd_resp.status_code != 200:
            # If update fails, attempt to abort. For this assignment we'll return error.
            return jsonify({"error": f"Failed to update inventory for product {product_id}"}), 500

    # Create order record (in-memory)
    order = create_order(customer_id, products, pricing_result)
    return jsonify(order), 201


@app.route("/api/orders/<int:order_id>", methods=["GET"])
def get_order_endpoint(order_id):
    order = get_order(order_id)
    if not order:
        return jsonify({"error": "Order not found"}), 404

    # Enrich with latest customer data (best-effort)
    try:
        cust_resp = requests.get(f"{CUSTOMER_SERVICE_URL}/{order['customer_id']}", timeout=HTTP_TIMEOUT)
        customer_data = cust_resp.json() if cust_resp.status_code == 200 else {"error": "Customer not found"}
    except requests.RequestException:
        customer_data = {"error": "Customer service unreachable"}

    result = {
        "order": order,
        "customer": customer_data
    }
    return jsonify(result), 200


@app.route("/api/orders", methods=["GET"])
def get_all_orders_endpoint():
    # optional query param filtering by customer_id
    customer_id = request.args.get("customer_id")
    if customer_id:
        return jsonify(get_orders_by_customer(customer_id)), 200
    return jsonify(get_all_orders()), 200


@app.route("/api/orders/customer/<int:customer_id>", methods=["GET"])
def get_orders_by_customer_endpoint(customer_id):
    return jsonify(get_orders_by_customer(customer_id)), 200





