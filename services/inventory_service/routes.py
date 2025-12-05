from flask import Flask, request, jsonify
import models

app = Flask(__name__)

@app.route("/api/inventory/items", methods=["GET"])
def list_items():
    data = models.get_all_items()
    return jsonify(data), 200


@app.route("/api/inventory/items", methods=["POST"])
def create_item():
    body = request.json
    if not body:
        return jsonify({"error": "Invalid JSON"}), 400

    name = body.get("name")
    quantity_available = body.get("quantity_available")
    unit_price = body.get("unit_price")

    if not name or quantity_available is None or unit_price is None:
        return jsonify({"error": "Missing required fields"}), 400

    models.add_item(name, quantity_available, unit_price)
    return jsonify({"message": "Item added"}), 201


@app.route("/api/inventory/check/<int:product_id>", methods=["GET"])
def check_stock_route(product_id):
    result = models.check_stock(product_id)
    if not result:
        return jsonify({"error": "Product not found"}), 404
    return jsonify(result), 200


@app.route("/api/inventory/update", methods=["PUT"])
def update_inventory_route():
    body = request.json
    if not body:
        return jsonify({"error": "Invalid JSON"}), 400

    product_id = body.get("product_id")
    quantity_sold = body.get("quantity_sold")

    if not product_id or quantity_sold is None:
        return jsonify({"error": "Missing product_id or quantity_sold"}), 400

    result = models.update_inventory(product_id, quantity_sold)
    
    if result == "insufficient":
        return jsonify({"error": "Not enough stock"}), 400
    if not result:
        return jsonify({"error": "Product not found"}), 404

    return jsonify({"message": "Inventory updated"}), 200

