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
    db.session.commit()

    # --- Products with real image URLs (Unsplash direct links) ---
    products = [
        Product(category_id=categories["vegetables"].id, name="Organic Broccoli",
                price=3.29, sale_price=2.49, unit="per bunch", stock_quantity=50,
                image_url="https://images.unsplash.com/photo-1584270354949-c26b0d5b4a0c?w=400"),
        Product(category_id=categories["vegetables"].id, name="Cherry Tomatoes",
                price=2.99, sale_price=None, unit="per 250g", stock_quantity=40,
                image_url="https://images.unsplash.com/photo-1592841200221-a6898f307baa?w=400"),

        Product(category_id=categories["fruits"].id, name="Fuji Apples",
                price=3.99, sale_price=None, unit="per kg", stock_quantity=60,
                image_url="https://images.unsplash.com/photo-1560806887-1e4cd0b6cbd6?w=400"),
        Product(category_id=categories["fruits"].id, name="Avocado",
                price=1.49, sale_price=None, unit="each", stock_quantity=80,
                image_url="https://images.unsplash.com/photo-1523049673857-eb18f1d7b578?w=400"),
        Product(category_id=categories["fruits"].id, name="Mixed Berries",
                price=6.99, sale_price=5.49, unit="per 300g", stock_quantity=25,
                image_url="https://images.unsplash.com/photo-1563746924237-f4471d3a0f83?w=400"),

        Product(category_id=categories["dairy"].id, name="Whole Milk",
                price=1.89, sale_price=None, unit="per liter", stock_quantity=70,
                image_url="https://images.unsplash.com/photo-1550583724-b2692b85b150?w=400"),
        Product(category_id=categories["dairy"].id, name="Greek Yogurt",
                price=3.99, sale_price=3.29, unit="per 500g", stock_quantity=35,
                image_url="https://images.unsplash.com/photo-1584278860047-22db9ff82bed?w=400"),
        Product(category_id=categories["dairy"].id, name="Cheddar Cheese",
                price=4.99, sale_price=None, unit="per 200g", stock_quantity=30,
                image_url="https://images.unsplash.com/photo-1618164436241-4473940d1f5c?w=400"),

        Product(category_id=categories["bakery"].id, name="Sourdough Bread",
                price=4.50, sale_price=None, unit="per loaf", stock_quantity=20,
                image_url="https://images.unsplash.com/photo-1585478259715-4d3a5d3bb4c5?w=400"),

        Product(category_id=categories["meat"].id, name="Chicken Breast",
                price=6.99, sale_price=None, unit="per 500g", stock_quantity=45,
                image_url="https://images.unsplash.com/photo-1604503468506-a8da13d82791?w=400"),

        Product(category_id=categories["beverages"].id, name="Orange Juice",
                price=3.49, sale_price=None, unit="per liter", stock_quantity=55,
                image_url="https://images.unsplash.com/photo-1600271886742-f049cd451bba?w=400"),
        Product(category_id=categories["beverages"].id, name="Almond Milk",
                price=2.99, sale_price=None, unit="per liter", stock_quantity=40,
                image_url="https://images.unsplash.com/photo-1600718374662-0483d2b9da44?w=400"),
    ]

    db.session.add_all(products)
    db.session.commit()

    print(f"Seeded {len(categories)} categories and {len(products)} products.")