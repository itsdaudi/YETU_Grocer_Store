# Users blueprint — handles profile info and saved addresses.
# All routes require a valid JWT, since "me" always refers to the
# logged-in user making the request.

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity

from app.models import db
from app.models.user import User
from app.models.address import Address

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

@users_bp.route("/me/addresses", methods=["GET"])
@jwt_required()
def get_addresses():
    user_id = get_jwt_identity()
    addresses = Address.query.filter_by(user_id=user_id).all()

    return jsonify({
        "addresses": [
            {
                "id": a.id,
                "label": a.label,
                "street": a.street,
                "city": a.city,
                "postal_code": a.postal_code,
                "is_default": a.is_default
            }
            for a in addresses
        ]
    }), 200


@users_bp.route("/me/addresses", methods=["POST"])
@jwt_required()
def create_address():
    user_id = get_jwt_identity()
    data = request.get_json() or {}

    street = data.get("street")
    city = data.get("city")

    if not street or not city:
        return jsonify({"error": "street and city are required"}), 400

    is_default = data.get("is_default", False)

    # if this new address is being set as default, unset any existing default
    if is_default:
        Address.query.filter_by(user_id=user_id, is_default=True).update({"is_default": False})

    new_address = Address(
        user_id=user_id,
        label=data.get("label"),
        street=street,
        city=city,
        postal_code=data.get("postal_code"),
        is_default=is_default
    )
    db.session.add(new_address)
    db.session.commit()

    return jsonify({
        "address": {
            "id": new_address.id,
            "label": new_address.label,
            "street": new_address.street,
            "city": new_address.city,
            "postal_code": new_address.postal_code,
            "is_default": new_address.is_default
        }
    }), 201


@users_bp.route("/me/addresses/<int:address_id>", methods=["PATCH"])
@jwt_required()
def update_address(address_id):
    user_id = get_jwt_identity()

    address = Address.query.filter_by(id=address_id, user_id=user_id).first()
    if not address:
        return jsonify({"error": "Address not found"}), 404

    data = request.get_json() or {}

    if "label" in data:
        address.label = data["label"]
    if "street" in data:
        address.street = data["street"]
    if "city" in data:
        address.city = data["city"]
    if "postal_code" in data:
        address.postal_code = data["postal_code"]

    if data.get("is_default") is True:
        # unset any other default address before making this one the default
        Address.query.filter_by(user_id=user_id, is_default=True).update({"is_default": False})
        address.is_default = True

    db.session.commit()

    return jsonify({
        "address": {
            "id": address.id,
            "label": address.label,
            "street": address.street,
            "city": address.city,
            "postal_code": address.postal_code,
            "is_default": address.is_default
        }
    }), 200


@users_bp.route("/me/addresses/<int:address_id>", methods=["DELETE"])
@jwt_required()
def delete_address(address_id):
    user_id = get_jwt_identity()

    address = Address.query.filter_by(id=address_id, user_id=user_id).first()
    if not address:
        return jsonify({"error": "Address not found"}), 404

    db.session.delete(address)
    db.session.commit()

    return jsonify({"message": "Address deleted"}), 200    