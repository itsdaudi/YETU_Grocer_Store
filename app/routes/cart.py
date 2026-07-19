# Cart blueprint — handles viewing and modifying the logged-in user's cart.
# Every route here requires a valid JWT, since a cart always belongs to
# a specific user.

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity

from app.models import db
from app.models.cart import Cart, CartItem
from app.models.product import Product

cart_bp = Blueprint("cart", __name__, url_prefix="/api/cart")

FREE_DELIVERY_THRESHOLD = 25.00
DELIVERY_FEE = 3.99


def get_or_create_cart(user_id):
    """Fetch the user's cart, creating an empty one if it doesn't exist yet."""
    cart = Cart.query.filter_by(user_id=user_id).first()
    if not cart:
        cart = Cart(user_id=user_id)
        db.session.add(cart)
        db.session.commit()
    return cart


def serialize_cart(cart):
    """Build the full cart response, including computed totals."""
    items = []
    subtotal = 0.0

    for item in cart.items:
        product = item.product
        # use sale price if one exists, otherwise regular price
        unit_price = float(product.sale_price) if product.sale_price else float(product.price)
        line_total = unit_price * item.quantity
        subtotal += line_total

        items.append({
            "id": item.id,
            "product_id": product.id,
            "name": product.name,
            "image_url": product.image_url,
            "unit": product.unit,
            "unit_price": unit_price,
            "quantity": item.quantity,
            "line_total": round(line_total, 2)
        })

    delivery_fee = 0.0 if subtotal >= FREE_DELIVERY_THRESHOLD else DELIVERY_FEE
    total = subtotal + delivery_fee

    return {
        "cart_id": cart.id,
        "items": items,
        "subtotal": round(subtotal, 2),
        "delivery_fee": round(delivery_fee, 2),
        "free_delivery_threshold": FREE_DELIVERY_THRESHOLD,
        "total": round(total, 2)
    }


@cart_bp.route("", methods=["GET"])
@jwt_required()
def get_cart():
    user_id = get_jwt_identity()
    cart = get_or_create_cart(user_id)

    return jsonify(serialize_cart(cart)), 200