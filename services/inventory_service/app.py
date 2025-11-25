from flask import Flask
app = Flask(__name__)

@app.route("/")
def home():
    return "Inventory Service is running!"

if __name__ == "__main__":
    app.run(port=5002)
