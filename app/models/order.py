from datetime import datetime
from app.models import db


class Order(db.Model):
    __tablename__ = "orders"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    address_id = db.Column(db.Integer, db.ForeignKey("addresses.id"), nullable=False)
    status = db.Column(db.String(20), nullable=False, default="processing")
    subtotal = db.Column(db.Numeric(10, 2), nullable=False)
    delivery_fee = db.Column(db.Numeric(10, 2), nullable=False, default=0)
    total = db.Column(db.Numeric(10, 2), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    user = db.relationship("User", backref="orders", lazy=True)
    address = db.relationship("Address")
    items = db.relationship("OrderItem", backref="order", lazy=True, cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Order {self.id} status={self.status}>"


class OrderItem(db.Model):
    __tablename__ = "order_items"

    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey("orders.id"), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey("products.id"), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    price_at_purchase = db.Column(db.Numeric(10, 2), nullable=False)

    product = db.relationship("Product")

    def __repr__(self):
        return f"<OrderItem product_id={self.product_id} qty={self.quantity}>"