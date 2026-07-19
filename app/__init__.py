from flask import Flask, jsonify
from flask_cors import CORS
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager
from app.models import db
from app.routes.auth import auth_bp
from app.routes.products import products_bp
from app.routes.cart import cart_bp


migrate = Migrate()
jwt = JWTManager()


def create_app():
    app = Flask(__name__)

    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///yetu.db"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["JWT_SECRET_KEY"] = "change-this-to-a-real-secret-later"  # temporary for dev

    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)

    CORS(app, origins=["http://localhost:5173"])

    # register blueprints — this is what actually wires up /api/auth/* routes
    app.register_blueprint(auth_bp)
    app.register_blueprint(products_bp)
    app.register_blueprint(cart_bp)

    @app.route("/")
    def index():
        return jsonify({"message": "Yetu Grocer Store API"})

    @app.route("/api/health")
    def health():
        return jsonify({"status": "ok"})

    return app