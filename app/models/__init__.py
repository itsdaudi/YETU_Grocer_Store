from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

from app.models.user import User
from app.models.category import Category
from app.models.product import Product
from app.models.address import Address

