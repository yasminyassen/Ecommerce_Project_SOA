from flask import Flask, jsonify
app = Flask(__name__)

@app.route("/")
def home():
    return "Inventory Service is running!"

@app.route("/test")
def test():
    return jsonify({"status": "inventory ok"})

if __name__ == "__main__":
    app.run(port=5002)
