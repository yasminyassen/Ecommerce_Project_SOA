from flask import Flask, jsonify
import requests

app = Flask(__name__)

INVENTORY_URL = "http://localhost:5002/test"

@app.route("/")
def home():
    # simple local response
    return "Pricing Service running"

@app.route("/check-inventory")
def check_inventory():
    try:
        resp = requests.get(INVENTORY_URL, timeout=5)
        resp.raise_for_status()  # raises for non-2xx
        data = resp.json()
        return jsonify({
            "status": "pricing -> inventory OK",
            "inventory_response": data
        })
    except requests.RequestException as e:
        return jsonify({
            "status": "pricing -> inventory FAILED",
            "error": str(e)
        }), 500

if __name__ == "__main__":
    app.run(port=5003)
