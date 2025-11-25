from flask import Flask
app = Flask(__name__)

@app.route("/")
def home():
    return "Customer Service is running!"

if __name__ == "__main__":
    app.run(port=5004)
