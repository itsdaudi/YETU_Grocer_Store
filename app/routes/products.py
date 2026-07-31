# Products blueprint — handles category listing and product browsing
# (list, filter, search, sort, pagination, single product detail).

from flask import Blueprint, request, jsonify
from app.models.category import Category
from app.models.product import Product
from app.utils.admin_required import admin_required
from app.models import db

products_bp = Blueprint("products", __name__, url_prefix="/api")


@products_bp.route("/categories", methods=["GET"])
def get_categories():
    categories = Category.query.all()

    return jsonify({
        "categories": [
            {"id": c.id, "name": c.name, "slug": c.slug}
            for c in categories
        ]
    }), 200


@products_bp.route("/products", methods=["GET"])
def get_products():
    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", 12, type=int)

    category_slug = request.args.get("category")
    search_term = request.args.get("search")
    sort = request.args.get("sort")

    query = Product.query

    if category_slug and category_slug.lower() != "all":
        query = query.join(Category).filter(Category.slug == category_slug)

    if search_term:
        query = query.filter(Product.name.ilike(f"%{search_term}%"))

    if sort == "price_asc":
        query = query.order_by(Product.price.asc())
    elif sort == "price_desc":
        query = query.order_by(Product.price.desc())

    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    products = pagination.items

    return jsonify({
        "products": [
            {
                "id": p.id,
                "name": p.name,
                "category_id": p.category_id,
                "category": p.category.name,
                "price": float(p.price),
                "sale_price": float(p.sale_price) if p.sale_price else None,
                "unit": p.unit,
                "image_url": p.image_url,
                "stock_quantity": p.stock_quantity
            }
            for p in products
        ],
        "total": pagination.total,
        "page": pagination.page,
        "per_page": pagination.per_page,
        "total_pages": pagination.pages
    }), 200

@products_bp.route("/products/<int:product_id>", methods=["GET"])
def get_product_detail(product_id):
    product = Product.query.get(product_id)

    if not product:
        return jsonify({"error": "Product not found"}), 404

    return jsonify({
        "product": {
            "id": product.id,
            "name": product.name,
            "category_id": product.category_id,
            "category": product.category.name,
            "price": float(product.price),
            "sale_price": float(product.sale_price) if product.sale_price else None,
            "unit": product.unit,
            "image_url": product.image_url,
            "description": product.description,
            "nutrition_info": product.nutrition_info,
            "stock_quantity": product.stock_quantity
        }
    }), 200    


@products_bp.route("/admin/products", methods=["POST"])
@admin_required
def create_product():
    data = request.get_json() or {}

    name = data.get("name")
    category_id = data.get("category_id")
    price = data.get("price")

    if not name or not category_id or price is None:
        return jsonify({"error": "name, category_id, and price are required"}), 400

    category = Category.query.get(category_id)
    if not category:
        return jsonify({"error": "Category not found"}), 404

    new_product = Product(
        name=name,
        category_id=category_id,
        price=price,
        sale_price=data.get("sale_price"),
        unit=data.get("unit"),
        image_url=data.get("image_url"),
        description=data.get("description"),
        nutrition_info=data.get("nutrition_info"),
        stock_quantity=data.get("stock_quantity", 0)
    )
    db.session.add(new_product)
    db.session.commit()

    return jsonify({
        "message": "Product created",
        "product": {
            "id": new_product.id,
            "name": new_product.name,
            "price": float(new_product.price),
            "stock_quantity": new_product.stock_quantity
        }
    }), 201    