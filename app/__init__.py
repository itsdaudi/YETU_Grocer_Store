from flask import Flask, jsonify
from flask_cors import CORS
from flask_migrate import Migrate
from app.models import db

migrate = Migrate()


def create_app():
    app = Flask(__name__)

    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///yetu.db"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    db.init_app(app)
    migrate.init_app(app, db)

    CORS(app, origins=["http://localhost:5173"])

    @app.route("/")
    def index():
        return jsonify({"message": "Yetu Grocer Store API"})

    @app.route("/api/health")
    def health():
        return jsonify({"status": "ok"})

    return app