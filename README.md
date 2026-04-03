# E-Commerce API

A FastAPI-based REST API with JWT authentication, RBAC, cursor-based pagination, rate limiting, Alembic migrations, cart/order management, and financial dashboard.

## Tech Stack

- **FastAPI** — web framework
- **SQLModel + SQLAlchemy** — ORM
- **SQLite** (aiosqlite) — database (swappable with PostgreSQL)
- **Alembic** — database migrations
- **SlowAPI** — rate limiting
- **python-jose** — JWT tokens
- **passlib** — password hashing

---

## Project Structure

```
├── alembic/                  # migration files
│   └── versions/
├── core/
│   ├── config.py             # settings (DATABASE_URL, SECRET_KEY, etc.)
│   ├── db.py                 # async engine & session
│   ├── security.py           # JWT, password hashing, RBAC
│   └── exceptions.py         # global error handler + integrity error parser
├── crud/
│   ├── user.py
│   ├── product.py
│   ├── review.py
│   ├── cart.py
│   ├── order.py
│   └── transaction.py
├── model/
│   ├── __init__.py           # exports all models
│   ├── enums.py              # Role, OrderStatus, TransactionType
│   ├── user.py               # User
│   ├── product.py            # Category, Product, Review
│   ├── cart.py               # CartItem
│   └── order.py              # Order, OrderItem, Transaction
├── routers/
│   ├── auth.py
│   ├── users.py
│   ├── products.py
│   ├── reviews.py
│   ├── cart.py
│   ├── orders.py
│   └── dashboard.py
├── schemas/
│   ├── user.py
│   ├── product.py
│   ├── review.py
│   ├── cart.py
│   ├── order.py
│   └── transaction.py
├── main.py
├── alembic.ini
└── requirements.txt
```

---

## Setup

```bash
# 1. Create and activate virtual environment
python -m venv .venv
.venv\Scripts\activate        # Windows
source .venv/bin/activate     # Linux/Mac

# 2. Install dependencies
pip install -r requirements.txt

# 3. Run migrations
alembic upgrade head

# 4. Start the server
uvicorn main:app --reload
```

API docs available at: `http://localhost:8000/docs`

---

## Environment Variables

Create a `.env` file in the root:

```env
DATABASE_URL=sqlite+aiosqlite:///./test.db
SECRET_KEY=your-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

For PostgreSQL:
```env
DATABASE_URL=postgresql+asyncpg://user:password@localhost/dbname
```

---

## RBAC — Roles

| Role | Permissions |
|---|---|
| `user` | Browse products, manage own cart, place orders, leave reviews, view own dashboard |
| `admin` | Everything + manage users, products, categories, all orders, full dashboard |

---

## API Endpoints

### Auth
| Method | Endpoint | Auth | Description |
|---|---|---|---|
| POST | `/seed-admin` | None | Create first admin (one-time only) |
| POST | `/auth/register` | None | Register as user |
| POST | `/auth/login` | None | Get JWT token |
| POST | `/auth/register-admin` | Admin | Create new admin |

### Users
| Method | Endpoint | Auth | Description |
|---|---|---|---|
| GET | `/users/me` | Any | Get current user info |
| GET | `/users/` | Admin | List all users (paginated) |
| PATCH | `/users/{id}/promote` | Admin | Promote user to admin |
| PATCH | `/users/{id}/toggle-active` | Admin | Activate / deactivate user |
| DELETE | `/users/{id}` | Admin | Delete user |

### Products
| Method | Endpoint | Auth | Description |
|---|---|---|---|
| GET | `/products/` | Any | List products (paginated) |
| GET | `/products/{id}` | Any | Get single product |
| POST | `/products/` | Admin | Create product |
| PATCH | `/products/{id}` | Admin | Update product |
| DELETE | `/products/{id}` | Admin | Delete product |
| GET | `/products/categories` | Any | List categories (paginated) |
| POST | `/products/categories` | Admin | Create category |
| DELETE | `/products/categories/{id}` | Admin | Delete category |

### Reviews
| Method | Endpoint | Auth | Description |
|---|---|---|---|
| GET | `/reviews/product/{id}` | Any | List reviews for a product (paginated) |
| POST | `/reviews/` | Any | Create review (one per user per product) |
| DELETE | `/reviews/{id}` | Owner or Admin | Delete review |

### Cart
| Method | Endpoint | Auth | Description |
|---|---|---|---|
| GET | `/cart/` | Any | View own cart |
| POST | `/cart/` | Any | Add item to cart |
| PATCH | `/cart/{item_id}` | Any | Update item quantity |
| DELETE | `/cart/{item_id}` | Any | Remove item from cart |

### Orders
| Method | Endpoint | Auth | Description |
|---|---|---|---|
| POST | `/orders/checkout` | Any | Checkout cart → create order + transaction |
| GET | `/orders/` | Any | View own orders (paginated) |
| GET | `/orders/all` | Admin | View all orders (paginated) |
| GET | `/orders/{id}` | Owner or Admin | Order detail with items |

### Dashboard
| Method | Endpoint | Auth | Description |
|---|---|---|---|
| GET | `/dashboard/transactions` | Any | Own transactions (with filters) |
| GET | `/dashboard/transactions/all` | Admin | All transactions (with filters) |
| GET | `/dashboard/summary` | Any | Own income, expense, net balance |
| GET | `/dashboard/summary/all` | Admin | Full system summary |
| GET | `/dashboard/by-category` | Any | Own category-wise totals |
| GET | `/dashboard/by-category/all` | Admin | Full category-wise totals |
| GET | `/dashboard/trends` | Any | Own monthly trends |
| GET | `/dashboard/trends/all` | Admin | Full monthly trends |
| GET | `/dashboard/recent` | Any | Own recent activity |
| GET | `/dashboard/recent/all` | Admin | All recent activity |

---

## Business Rules

- A user can only submit **one review per product**
- A product can only appear **once per cart**
- Checkout creates an **Order + Transaction** automatically and clears the cart
- **Transactions are immutable** — no update or delete. A reversal transaction can be created to offset incorrect entries
- Deleting a category also deletes all its products (CASCADE)
- Deleting a product also deletes all its reviews (CASCADE)
- Deleting a user also deletes all their data (CASCADE)
- Deactivated users get `403` on login
- Only review owner or admin can delete a review

---

## Pagination

All list endpoints use **cursor-based pagination** — stable even when records are added or deleted.

```bash
GET /products/              # first page
GET /products/?cursor=42    # next page using next_cursor from previous response
```

Response format:
```json
{
  "data": [...],
  "next_cursor": 42,
  "has_more": true
}
```

---

## Dashboard Filters

Transaction endpoints support query param filters:

```bash
GET /dashboard/transactions?type=expense
GET /dashboard/transactions?category=order
GET /dashboard/transactions?date_from=2026-01-01&date_to=2026-03-31
```

---

## Error Handling

| Situation | Status | Example |
|---|---|---|
| Duplicate name/email | `400` | "A record with this name already exists." |
| Already reviewed | `400` | "You have already reviewed this product." |
| Empty cart checkout | `400` | "Your cart is empty." |
| Invalid ID | `404` | "Product not found." |
| No permission | `403` | "You are not allowed to delete this review." |
| Deactivated account | `403` | "Account is deactivated." |
| Wrong credentials | `401` | "Invalid username or password." |
| DB/server error | `500` | "Failed to create product. Please try again." |

---

## Rate Limiting

- Global: **100 requests/minute** per IP
- `/` root: **10 requests/minute** per IP

Returns `429 Too Many Requests` when exceeded.

---

## Data Persistence

SQLite with `aiosqlite` async driver. Foreign key enforcement enabled via `PRAGMA foreign_keys=ON`. Schema managed via Alembic migrations.

To switch to PostgreSQL, update `DATABASE_URL` in `.env`:
```env
DATABASE_URL=postgresql+asyncpg://user:password@localhost/dbname
```

---

## Alembic Migrations

```bash
alembic upgrade head                              # apply all migrations
alembic revision --autogenerate -m "description" # generate new migration
alembic downgrade -1                              # rollback one step
alembic current                                   # check current state
alembic history                                   # view migration history
```

---

## First Time Setup Flow

```
1. POST /seed-admin                → create first admin (no auth needed)
2. POST /auth/login                → get admin JWT
3. POST /products/categories       → create categories
4. POST /products/                 → create products
5. POST /auth/register             → register normal users
6. POST /cart/                     → add products to cart
7. POST /orders/checkout           → place order
8. GET  /dashboard/summary         → view financial summary
```
