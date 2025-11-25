from flask import Flask
app = Flask(__name__)

@app.route("/")
def home():
    return "Order Service is running"

app.run(port=5001)
