cat > README.md << 'EOF'
# Yetu Grocer Store — Backend API

Yetu is a full-stack grocery delivery web application. This repository contains the Flask REST API backend that powers the Yetu React frontend — handling authentication, product browsing, cart management, checkout, order tracking, and admin order management.

## Live Demo

- **Frontend:** https://yetu-grocer-store-frontend.vercel.app
- **API:** https://yetu-grocer-store.onrender.com

## Features

### Authentication & Authorization
- User signup, login, and session persistence via JWT (JSON Web Tokens)
- Role-based access control — regular customers vs. admin users
- Protected admin-only routes for store management

### Product Management
- Browse product catalog with pagination
- Search products by name
- Filter products by category
- Sort products by price
- View individual product details

### Shopping Cart
- Add, update, and remove items from cart
- Server-side stock validation
- Real-time cart total calculation

### Order Management
- Atomic order creation (stock decrement + order creation with rollback on failure)
- View order history with detailed breakdown
- Reorder items from past orders
- Admin dashboard support — view all orders across all customers
- Update order status (admin only)

### User Profile
- Manage personal information
- Save multiple delivery addresses
- View order history

## Tech Stack

| Component | Technology |
|-----------|------------|
| Framework | Flask |
| Database | PostgreSQL |
| ORM | Flask-SQLAlchemy |
| Migrations | Flask-Migrate (Alembic) |
| Authentication | Flask-JWT-Extended |
| Password Hashing | Werkzeug |
| CORS | Flask-CORS |
| Deployment | Render |
| Production Server | Gunicorn |

## Database Models

| Model | Description |
|-------|-------------|
| User | Account info, hashed password, role (customer/admin) |
| Category | Product categories (Vegetables, Fruits, Dairy, etc.) |
| Product | Catalog items with price, sale price, stock, and category |
| Address | User's saved delivery addresses |
| Cart / CartItem | Current shopping cart per user |
| Order / OrderItem | Placed orders with price locked at purchase time |

## Installation & Setup

### Prerequisites
- Python 3.12+
- PostgreSQL (running locally)
- Pipenv

### 1. Clone the repository
```bash
git clone https://github.com/itsdaudi/YETU_Grocer_Store.git
cd YETU_Grocer_Store
```

### 2. Install dependencies
```bash
pipenv install
pipenv shell
```

### 3. Set up environment variables

Create a `.env` file:
Create a `.flaskenv` file:

### 4. Set up the database
```bash
flask db upgrade
python3 seed.py
```

### 5. Run the development server
```bash
python3 run.py
```

The API runs at `http://127.0.0.1:5000`.

## API Overview

| Endpoint | Method | Description |
|---|---|---|
| `/api/auth/signup` | POST | Create a new account |
| `/api/auth/login` | POST | Log in and receive a JWT |
| `/api/auth/me` | GET | Get the current logged-in user |
| `/api/categories` | GET | List all product categories |
| `/api/products` | GET | List products (supports category/search/sort/pagination) |
| `/api/products/<id>` | GET | Get a single product's details |
| `/api/cart` | GET | View current user's cart |
| `/api/cart/items` | POST | Add an item to the cart |
| `/api/cart/items/<id>` | PATCH / DELETE | Update or remove a cart item |
| `/api/orders` | POST / GET | Place an order / view order history |
| `/api/orders/<id>` | GET | View a single order's details |
| `/api/orders/<id>/reorder` | POST | Reorder items from a past order |
| `/api/orders/admin/all` | GET | (Admin only) View all orders |
| `/api/orders/admin/<id>/status` | PATCH | (Admin only) Update order status |
| `/api/users/me` | GET / PATCH | View or update profile |
| `/api/users/me/addresses` | GET / POST | List or add delivery addresses |
| `/api/users/me/addresses/<id>` | PATCH / DELETE | Update or delete an address |

## Related Repository

Frontend (React + Vite): https://github.com/itsdaudi/yetu_grocer_store_frontend

## Author

Daudi Kazungu
EOF