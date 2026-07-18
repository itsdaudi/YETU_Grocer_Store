from flask import Flask, jsonify
from flask_cors import CORS
from flask_migrate import Migrate
from app.models import db
from flask_jwt_extended import JWTManager

migrate = Migrate()
jwt = JWTManager()


def create_app():
    app = Flask(__name__)

    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///yetu.db"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)

    CORS(app, origins=["http://localhost:5173"])

    @app.route("/")
    def index():
        return jsonify({"message": "Yetu Grocer Store API"})

    @app.route("/api/health")
    def health():
        return jsonify({"status": "ok"})

    return app