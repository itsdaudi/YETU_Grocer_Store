# Auth blueprint — handles signup, login, and returning the current user's info.

from flask import Blueprint, request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from app.models import db
from app.models.user import User

auth_bp = Blueprint("auth", __name__, url_prefix="/api/auth")


@auth_bp.route("/signup", methods=["POST"])
def signup():
    data = request.get_json() or {}

    name = data.get("name")
    email = data.get("email","").strip().lower()  # normalize email to lowercase
    password = data.get("password")

    # basic validation — reject if any required field is missing
    if not name or not email or not password:
        return jsonify({"error": "name, email, and password are required"}), 400

    # prevent duplicate accounts
    existing_user = User.query.filter_by(email=email).first()
    if existing_user:
        return jsonify({"error": "An account with this email already exists"}), 409

    # hash the password — never store plain text
    hashed_password = generate_password_hash(password)

    new_user = User(name=name, email=email, password_hash=hashed_password)
    db.session.add(new_user)
    db.session.commit()

    # issue a JWT immediately so the user is logged in right after signup
    access_token = create_access_token(identity=str(new_user.id))

    return jsonify({
        "message": "Account created successfully",
        "access_token": access_token,
        "user": {
            "id": new_user.id,
            "name": new_user.name,
            "email": new_user.email,
            "role": new_user.role
        }
    }), 201

@auth_bp.route("/login", methods=["POST"])
def login():
    data = request.get_json() or {}

    email = data.get("email","").strip().lower()  # normalize email to lowercase   
    password = data.get("password")

    if not email or not password:
        return jsonify({"error": "email and password are required"}), 400

    user = User.query.filter_by(email=email).first()

    # check both that the user exists AND the password matches —
    # done in one condition so we don't leak whether the email exists
    if not user or not check_password_hash(user.password_hash, password):
        return jsonify({"error": "Invalid email or password"}), 401

    access_token = create_access_token(identity=str(user.id))

    return jsonify({
        "message": "Login successful",
        "access_token": access_token,
        "user": {
            "id": user.id,
            "name": user.name,
            "email": user.email,
            "role": user.role
        }
    }), 200  

@auth_bp.route("/me", methods=["GET"])
@jwt_required()
def me():
    # get_jwt_identity() pulls the user id we stored in the token at login/signup
    user_id = get_jwt_identity()
    user = User.query.get(user_id)

    if not user:
        return jsonify({"error": "User not found"}), 404

    return jsonify({
        "user": {
            "id": user.id,
            "name": user.name,
            "email": user.email,
            "role": user.role
        }
    }), 200



