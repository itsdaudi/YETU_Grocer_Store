# Orders blueprint — handles checkout (cart -> order) and order history.

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.utils.admin_required import admin_required
from sqlalchemy import func
from app.models.product import Product


from app.models import db
from app.models.cart import Cart, CartItem
from app.models.order import Order, OrderItem
from app.models.address import Address

orders_bp = Blueprint("orders", __name__, url_prefix="/api/orders")

FREE_DELIVERY_THRESHOLD = 25.00
DELIVERY_FEE = 3.99


@orders_bp.route("", methods=["POST"])
@jwt_required()
def create_order():
    user_id = get_jwt_identity()

    data = request.get_json() or {}
    address_id = data.get("address_id")

    if not address_id:
        return jsonify({"error": "address_id is required"}), 400

    # confirm the address belongs to this user
    address = Address.query.filter_by(id=address_id, user_id=user_id).first()
    if not address:
        return jsonify({"error": "Address not found"}), 404

    cart = Cart.query.filter_by(user_id=user_id).first()
    if not cart or not cart.items:
        return jsonify({"error": "Cart is empty"}), 400

    # --- validate stock for every item BEFORE making any changes ---
    for item in cart.items:
        if item.quantity > item.product.stock_quantity:
            return jsonify({
                "error": f"Only {item.product.stock_quantity} of {item.product.name} available in stock"
            }), 400

    # --- calculate totals ---
    subtotal = sum(
        (float(item.product.sale_price) if item.product.sale_price else float(item.product.price))
        * item.quantity
        for item in cart.items
    )
    delivery_fee = 0.0 if subtotal >= FREE_DELIVERY_THRESHOLD else DELIVERY_FEE
    total = subtotal + delivery_fee

    try:
        # --- create the order ---
        order = Order(
            user_id=user_id,
            address_id=address_id,
            status="processing",
            subtotal=round(subtotal, 2),
            delivery_fee=round(delivery_fee, 2),
            total=round(total, 2)
        )
        db.session.add(order)
        db.session.flush()  # assigns order.id without fully committing yet

        # --- copy cart items into order items, locking in current prices ---
        for item in cart.items:
            unit_price = float(item.product.sale_price) if item.product.sale_price else float(item.product.price)

            order_item = OrderItem(
                order_id=order.id,
                product_id=item.product_id,
                quantity=item.quantity,
                price_at_purchase=round(unit_price, 2)
            )
            db.session.add(order_item)

            # decrement stock
            item.product.stock_quantity -= item.quantity

        # --- clear the cart ---
        for item in cart.items:
            db.session.delete(item)

        db.session.commit()  # everything succeeds together, or nothing does

    except Exception as e:
        db.session.rollback()  # undo everything if ANYTHING above failed
        return jsonify({"error": "Failed to create order", "details": str(e)}), 500

    return jsonify({
        "message": "Order placed successfully",
        "order": {
            "id": order.id,
            "status": order.status,
            "subtotal": float(order.subtotal),
            "delivery_fee": float(order.delivery_fee),
            "total": float(order.total),
            "created_at": order.created_at.isoformat()
        }
    }), 201

@orders_bp.route("", methods=["GET"])
@jwt_required()
def get_orders():
    user_id = get_jwt_identity()
    status_filter = request.args.get("status")

    query = Order.query.filter_by(user_id=user_id)

    if status_filter:
        query = query.filter_by(status=status_filter)

    orders = query.order_by(Order.created_at.desc()).all()

    return jsonify({
        "orders": [
            {
                "id": o.id,
                "status": o.status,
                "subtotal": float(o.subtotal),
                "delivery_fee": float(o.delivery_fee),
                "total": float(o.total),
                "item_count": len(o.items),
                "created_at": o.created_at.isoformat()
            }
            for o in orders
        ]
    }), 200

@orders_bp.route("/<int:order_id>", methods=["GET"])
@jwt_required()
def get_order_detail(order_id):
    user_id = get_jwt_identity()

    order = Order.query.filter_by(id=order_id, user_id=user_id).first()
    if not order:
        return jsonify({"error": "Order not found"}), 404

    return jsonify({
        "order": {
            "id": order.id,
            "status": order.status,
            "subtotal": float(order.subtotal),
            "delivery_fee": float(order.delivery_fee),
            "total": float(order.total),
            "created_at": order.created_at.isoformat(),
            "address": {
                "label": order.address.label,
                "street": order.address.street,
                "city": order.address.city
            },
            "items": [
                {
                    "product_id": item.product_id,
                    "name": item.product.name,
                    "image_url": item.product.image_url,
                    "quantity": item.quantity,
                    "price_at_purchase": float(item.price_at_purchase)
                }
                for item in order.items
            ]
        }
    }), 200 


@orders_bp.route("/<int:order_id>/reorder", methods=["POST"])
@jwt_required()
def reorder(order_id):
    user_id = get_jwt_identity()

    # only allow reordering an order that actually belongs to this user
    order = Order.query.filter_by(id=order_id, user_id=user_id).first()
    if not order:
        return jsonify({"error": "Order not found"}), 404

    # get (or create) the user's current cart to add items into
    cart = Cart.query.filter_by(user_id=user_id).first()
    if not cart:
        cart = Cart(user_id=user_id)
        db.session.add(cart)
        db.session.flush()  # assigns cart.id before we use it below

    added = []     # product names successfully added back to the cart
    skipped = []   # product names skipped because they're fully out of stock

    for item in order.items:
        product = item.product

        # skip products that no longer have any stock at all
        if product.stock_quantity < 1:
            skipped.append(product.name)
            continue

        # don't re-add more than what's currently in stock, even if the
        # original order had a higher quantity
        quantity_to_add = min(item.quantity, product.stock_quantity)

        # check if this product is already sitting in the cart
        existing_cart_item = CartItem.query.filter_by(
            cart_id=cart.id, product_id=product.id
        ).first()

        if existing_cart_item:
            # merge quantities instead of creating a duplicate row,
            # still capped at available stock
            existing_cart_item.quantity = min(
                existing_cart_item.quantity + quantity_to_add,
                product.stock_quantity
            )
        else:
            # no existing row for this product — create a new cart item
            db.session.add(CartItem(
                cart_id=cart.id,
                product_id=product.id,
                quantity=quantity_to_add
            ))

        added.append(product.name)

    db.session.commit()

    return jsonify({
        "message": "Items added to cart",
        "added": added,
        "skipped_out_of_stock": skipped
    }), 200 

@orders_bp.route("/admin/all", methods=["GET"])
@admin_required
def get_all_orders():
    status_filter = request.args.get("status")

    query = Order.query

    if status_filter:
        query = query.filter_by(status=status_filter)

    orders = query.order_by(Order.created_at.desc()).all()

    return jsonify({
        "orders": [
            {
                "id": o.id,
                "customer_name": o.user.name,
                "customer_email": o.user.email,
                "status": o.status,
                "subtotal": float(o.subtotal),
                "delivery_fee": float(o.delivery_fee),
                "total": float(o.total),
                "item_count": len(o.items),
                "created_at": o.created_at.isoformat()
            }
            for o in orders
        ]
    }), 200


@orders_bp.route("/admin/<int:order_id>/status", methods=["PATCH"])
@admin_required
def update_order_status(order_id):
    order = Order.query.get(order_id)
    if not order:
        return jsonify({"error": "Order not found"}), 404

    data = request.get_json() or {}
    new_status = data.get("status")

    valid_statuses = ["processing", "packed", "in_transit", "delivered"]
    if new_status not in valid_statuses:
        return jsonify({
            "error": f"status must be one of: {', '.join(valid_statuses)}"
        }), 400

    order.status = new_status
    db.session.commit()

    return jsonify({
        "message": "Order status updated",
        "order": {
            "id": order.id,
            "status": order.status
        }
    }), 200 


@orders_bp.route("/admin/stats", methods=["GET"])
@admin_required
def admin_stats():
    total_orders = Order.query.count()

    # Total revenue (sum of all order totals)
    revenue_result = db.session.query(func.coalesce(func.sum(Order.total), 0)).scalar()
    total_revenue = float(revenue_result)

    # Orders by status
    status_counts = (
        db.session.query(Order.status, func.count(Order.id))
        .group_by(Order.status)
        .all()
    )
    orders_by_status = {status: count for status, count in status_counts}

    # Low stock products (stock < 10)
    low_stock_count = Product.query.filter(Product.stock_quantity < 10).count()

    # Recent orders (last 5)
    recent_orders = (
        Order.query
        .order_by(Order.created_at.desc())
        .limit(5)
        .all()
    )

    return jsonify({
        "total_orders": total_orders,
        "total_revenue": total_revenue,
        "orders_by_status": orders_by_status,
        "low_stock_count": low_stock_count,
        "recent_orders": [
            {
                "id": o.id,
                "customer_name": o.user.name,
                "total": float(o.total),
                "status": o.status,
                "created_at": o.created_at.isoformat(),
            }
            for o in recent_orders
        ],
    }), 200

