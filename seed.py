# Seed script — populates the database with sample categories and products
# for local development and testing. Safe to re-run: it clears existing
# categories/products first so you don't end up with duplicates.

from app import create_app
from app.models import db
from app.models.category import Category
from app.models.product import Product

app = create_app()

with app.app_context():
    # Clear existing data first (products before categories, since products
    # depend on categories via foreign key)
    Product.query.delete()
    Category.query.delete()
    db.session.commit()

    # --- Categories ---
    categories = {
        "vegetables": Category(name="Vegetables", slug="vegetables"),
        "fruits": Category(name="Fruits", slug="fruits"),
        "dairy": Category(name="Dairy", slug="dairy"),
        "bakery": Category(name="Bakery", slug="bakery"),
        "meat": Category(name="Meat", slug="meat"),
        "beverages": Category(name="Beverages", slug="beverages"),
        "snacks": Category(name="Snacks", slug="snacks"),
    }

    db.session.add_all(categories.values())
    db.session.commit()  # commit now so categories get real IDs before we link products

    # --- Products (matches the Figma design's sample data) ---
    products = [
        Product(category_id=categories["vegetables"].id, name="Organic Broccoli",
                price=3.29, sale_price=2.49, unit="per bunch", stock_quantity=50,
                image_url="https://example.com/broccoli.jpg"),
        Product(category_id=categories["vegetables"].id, name="Cherry Tomatoes",
                price=2.99, sale_price=None, unit="per 250g", stock_quantity=40,
                image_url="https://example.com/tomatoes.jpg"),

        Product(category_id=categories["fruits"].id, name="Fuji Apples",
                price=3.99, sale_price=None, unit="per kg", stock_quantity=60,
                image_url="https://example.com/apples.jpg"),
        Product(category_id=categories["fruits"].id, name="Avocado",
                price=1.49, sale_price=None, unit="each", stock_quantity=80,
                image_url="https://example.com/avocado.jpg"),
        Product(category_id=categories["fruits"].id, name="Mixed Berries",
                price=6.99, sale_price=5.49, unit="per 300g", stock_quantity=25,
                image_url="https://example.com/berries.jpg"),

        Product(category_id=categories["dairy"].id, name="Whole Milk",
                price=1.89, sale_price=None, unit="per liter", stock_quantity=70,
                image_url="https://example.com/milk.jpg"),
        Product(category_id=categories["dairy"].id, name="Greek Yogurt",
                price=3.99, sale_price=3.29, unit="per 500g", stock_quantity=35,
                image_url="https://example.com/yogurt.jpg"),
        Product(category_id=categories["dairy"].id, name="Cheddar Cheese",
                price=4.99, sale_price=None, unit="per 200g", stock_quantity=30,
                image_url="https://example.com/cheese.jpg"),

        Product(category_id=categories["bakery"].id, name="Sourdough Bread",
                price=4.50, sale_price=None, unit="per loaf", stock_quantity=20,
                image_url="https://example.com/sourdough.jpg"),

        Product(category_id=categories["meat"].id, name="Chicken Breast",
                price=6.99, sale_price=None, unit="per 500g", stock_quantity=45,
                image_url="https://example.com/chicken.jpg"),

        Product(category_id=categories["beverages"].id, name="Orange Juice",
                price=3.49, sale_price=None, unit="per liter", stock_quantity=55,
                image_url="https://example.com/oj.jpg"),
        Product(category_id=categories["beverages"].id, name="Almond Milk",
                price=2.99, sale_price=None, unit="per liter", stock_quantity=40,
                image_url="https://example.com/almond-milk.jpg"),
    ]

    db.session.add_all(products)
    db.session.commit()

    print(f"Seeded {len(categories)} categories and {len(products)} products.")