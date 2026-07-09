from flask import Flask, jsonify
from flask_cors import CORS

def create_app():
    app = Flask(__name__)
    CORS(app, origins=["http://localhost:3000"])

    @app.route("/api/health")
    def health():
        return jsonify({"status": "ok"})

    return app