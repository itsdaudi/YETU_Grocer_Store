# Users blueprint — handles profile info and saved addresses.
# All routes require a valid JWT, since "me" always refers to the
# logged-in user making the request.

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity

from app.models import db
from app.models.user import User

users_bp = Blueprint("users", __name__, url_prefix="/api/users")


@users_bp.route("/me", methods=["GET"])
@jwt_required()
def get_profile():
    user_id = get_jwt_identity()
    user = User.query.get(user_id)

    if not user:
        return jsonify({"error": "User not found"}), 404

    return jsonify({
        "user": {
            "id": user.id,
            "name": user.name,
            "email": user.email,
            "created_at": user.created_at.isoformat()
        }
    }), 200


@users_bp.route("/me", methods=["PATCH"])
@jwt_required()
def update_profile():
    user_id = get_jwt_identity()
    user = User.query.get(user_id)

    if not user:
        return jsonify({"error": "User not found"}), 404

    data = request.get_json() or {}
    new_name = data.get("name")
    new_email = data.get("email")

    if new_name:
        user.name = new_name

    if new_email and new_email != user.email:
        # make sure no other user already has this email
        existing = User.query.filter_by(email=new_email).first()
        if existing:
            return jsonify({"error": "That email is already in use"}), 409
        user.email = new_email

    db.session.commit()

    return jsonify({
        "user": {
            "id": user.id,
            "name": user.name,
            "email": user.email
        }
    }), 200