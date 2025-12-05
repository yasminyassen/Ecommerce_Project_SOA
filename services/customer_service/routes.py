from flask import Flask, request, jsonify
import models

app = Flask(__name__)

@app.route("/api/customers/<int:customer_id>", methods=["GET"])
def get_customer(customer_id):
    customer = models.get_customer(customer_id)
    if not customer:
        return jsonify({"error": "Customer not found"}), 404
    return jsonify(customer), 200


@app.route("/api/customers/<int:customer_id>/orders", methods=["GET"])
def get_customer_orders(customer_id):
    customer = models.get_customer(customer_id)
    if not customer:
        return jsonify({"error": "Customer not found"}), 404
    orders = models.get_customer_orders(customer_id)
    return jsonify(orders), 200


@app.route("/api/customers/<int:customer_id>/loyalty", methods=["PUT"])
def update_loyalty(customer_id):
    body = request.get_json()
    if not body:
        return jsonify({"error": "Invalid JSON"}), 400

    points = body.get("points")
    if points is None:
        return jsonify({"error": "Missing points value"}), 400
    try:
        points_int = int(points)
    except (TypeError, ValueError):
        return jsonify({"error": "Points must be integer"}), 400

    customer = models.get_customer(customer_id)
    if not customer:
        return jsonify({"error": "Customer not found"}), 404

    ok = models.update_loyalty_points(customer_id, points_int)
    if not ok:
        return jsonify({"error": "Failed to update loyalty points (DB error)"}), 500

    return jsonify({"message": "Loyalty points updated"}), 200


