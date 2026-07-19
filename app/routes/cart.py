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

@cart_bp.route("/items", methods=["POST"])
@jwt_required()
def add_cart_item():
    user_id = get_jwt_identity()
    cart = get_or_create_cart(user_id)

    data = request.get_json() or {}
    product_id = data.get("product_id")
    quantity = data.get("quantity", 1)

    if not product_id:
        return jsonify({"error": "product_id is required"}), 400

    if not isinstance(quantity, int) or quantity < 1:
        return jsonify({"error": "quantity must be a positive integer"}), 400

    product = Product.query.get(product_id)
    if not product:
        return jsonify({"error": "Product not found"}), 404

    # check if this product is already in the cart
    existing_item = CartItem.query.filter_by(cart_id=cart.id, product_id=product_id).first()

    if existing_item:
        new_quantity = existing_item.quantity + quantity
        if new_quantity > product.stock_quantity:
            return jsonify({
                "error": f"Only {product.stock_quantity} of {product.name} available in stock"
            }), 400
        existing_item.quantity = new_quantity
    else:
        if quantity > product.stock_quantity:
            return jsonify({
                "error": f"Only {product.stock_quantity} of {product.name} available in stock"
            }), 400
        new_item = CartItem(cart_id=cart.id, product_id=product_id, quantity=quantity)
        db.session.add(new_item)

    db.session.commit()

    return jsonify(serialize_cart(cart)), 201

@cart_bp.route("/items/<int:item_id>", methods=["PATCH"])
@jwt_required()
def update_cart_item(item_id):
    user_id = get_jwt_identity()
    cart = get_or_create_cart(user_id)

    item = CartItem.query.filter_by(id=item_id, cart_id=cart.id).first()
    if not item:
        return jsonify({"error": "Cart item not found"}), 404

    data = request.get_json() or {}
    quantity = data.get("quantity")

    if not isinstance(quantity, int) or quantity < 1:
        return jsonify({"error": "quantity must be a positive integer"}), 400

    if quantity > item.product.stock_quantity:
        return jsonify({
            "error": f"Only {item.product.stock_quantity} of {item.product.name} available in stock"
        }), 400

    item.quantity = quantity
    db.session.commit()

    return jsonify(serialize_cart(cart)), 200 

@cart_bp.route("/items/<int:item_id>", methods=["DELETE"])
@jwt_required()
def delete_cart_item(item_id):
    user_id = get_jwt_identity()
    cart = get_or_create_cart(user_id)

    item = CartItem.query.filter_by(id=item_id, cart_id=cart.id).first()
    if not item:
        return jsonify({"error": "Cart item not found"}), 404

    db.session.delete(item)
    db.session.commit()

    return jsonify(serialize_cart(cart)), 200  