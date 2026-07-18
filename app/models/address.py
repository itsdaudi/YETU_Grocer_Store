from app.models import db


class Address(db.Model):
    __tablename__ = "addresses"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    label = db.Column(db.String(60), nullable=True)  # e.g. "Home", "Work"
    street = db.Column(db.String(200), nullable=False)
    city = db.Column(db.String(100), nullable=False)
    postal_code = db.Column(db.String(20), nullable=True)
    is_default = db.Column(db.Boolean, default=False)

    user = db.relationship("User", backref="addresses", lazy=True)

    def __repr__(self):
        return f"<Address {self.label or self.street}>"