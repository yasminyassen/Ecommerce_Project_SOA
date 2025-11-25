from flask import Flask
app = Flask(__name__)

@app.route("/")
def home():
    return "Pricing Service is running!"

if __name__ == "__main__":
    app.run(port=5003)
