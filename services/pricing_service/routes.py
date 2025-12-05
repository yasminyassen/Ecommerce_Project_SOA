from flask import Flask, request, jsonify
import requests
import models

app = Flask(__name__)

INVENTORY_SERVICE_URL = "http://localhost:5002/api/inventory"
HTTP_TIMEOUT = 5

@app.route("/api/pricing/calculate", methods=["POST"])
def calculate_price():
    data = request.get_json()
    if not data or "products" not in data:
        return jsonify({"error": "Invalid input, products list required"}), 400

    products = data["products"]
    if not isinstance(products, list) or len(products) == 0:
        return jsonify({"error": "Products must be a non-empty list"}), 400

    region = data.get("region", "Default")

    items = []
    total_before_tax = 0.0
    total_discount = 0.0

    # For each product, get base info from Inventory Service
    for p in products:
        try:
            product_id = int(p.get("product_id"))
            qty = int(p.get("quantity", 0))
        except Exception:
            return jsonify({"error": "Invalid product structure"}), 400

        if qty <= 0:
            return jsonify({"error": f"Invalid quantity for product {product_id}"}), 400

        # Call inventory to get unit price and availability
        try:
            resp = requests.get(f"{INVENTORY_SERVICE_URL}/check/{product_id}", timeout=HTTP_TIMEOUT)
        except requests.RequestException:
            return jsonify({"error": "Inventory service unreachable"}), 502

        if resp.status_code != 200:
            return jsonify({"error": f"Product {product_id} not found in inventory"}), 404

        prod_data = resp.json()
        unit_price = float(prod_data.get("unit_price", 0.0))
        available = int(prod_data.get("quantity_available", 0))

        subtotal = unit_price * qty
        applied_discount = 0.0

        # apply best pricing rule
        rules = models.get_pricing_rules_for_product(product_id)
        best_discount = 0.0
        for r in rules:
            try:
                min_q = int(r.get("min_quantity", 0))
                disc = float(r.get("discount_percentage", 0.0))
                if qty >= min_q and disc > best_discount:
                    best_discount = disc
            except Exception:
                continue

        if best_discount > 0:
            applied_discount = subtotal * (best_discount / 100.0)
            subtotal_after_discount = subtotal - applied_discount
        else:
            subtotal_after_discount = subtotal

        items.append({
            "product_id": product_id,
            "quantity": qty,
            "unit_price": round(unit_price, 2),
            "available": available,
            "subtotal": round(subtotal, 2),
            "discount_percentage": round(best_discount, 2),
            "discount_amount": round(applied_discount, 2),
            "subtotal_after_discount": round(subtotal_after_discount, 2)
        })

        total_before_tax += subtotal_after_discount
        total_discount += applied_discount

    # get tax rate
    tax_rate = models.get_tax_rate(region)
    if tax_rate is None:
        # try Default region
        tax_rate = models.get_tax_rate("Default") or 0.0

    tax_amount = total_before_tax * (tax_rate / 100.0)
    total_amount = total_before_tax + tax_amount

    result = {
        "items": items,
        "total_before_tax": round(total_before_tax, 2),
        "total_discount": round(total_discount, 2),
        "tax_rate": round(tax_rate, 2),
        "tax_amount": round(tax_amount, 2),
        "total_amount": round(total_amount, 2)
    }
    return jsonify(result), 200
