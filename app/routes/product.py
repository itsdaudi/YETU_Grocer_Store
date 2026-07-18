# Products blueprint — handles category listing and product browsing
# (list, filter, search, sort, pagination, single product detail).

from flask import Blueprint, request, jsonify
from app.models.category import Category

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