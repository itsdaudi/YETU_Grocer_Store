from flask import Flask, jsonify
from flask_cors import CORS

@app.route("/")
def index():
    return jsonify({"message": "Yetu Grocer Store API"})

def create_app():
    app = Flask(__name__)
    CORS(app, origins=["http://localhost:5000"])

    @app.route("/api/health")
    def health():
        return jsonify({"status": "ok"})

    return app