# Products blueprint — handles category listing and product browsing
# (list, filter, search, sort, pagination, single product detail).

from flask import Blueprint, request, jsonify
from app.models.category import Category
from app.models.product import Product

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