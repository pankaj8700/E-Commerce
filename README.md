# E-Commerce API

A FastAPI-based REST API with JWT authentication, RBAC, cursor-based pagination, rate limiting, Alembic migrations, cart/order management, and financial dashboard.

## Tech Stack

- **FastAPI** — web framework
- **SQLModel + SQLAlchemy** — ORM
- **SQLite** (aiosqlite) — database (swappable with PostgreSQL)
- **Alembic** — database migrations
- **SlowAPI** — rate limiting
- **python-jose** — JWT tokens
- **passlib[bcrypt]** — password hashing

---

## Project Structure

```
├── alembic/                  # migration files
│   └── versions/
├── core/
│   ├── config.py             # settings (DATABASE_URL, SECRET_KEY, etc.)
│   ├── db.py                 # async engine & session
│   ├── dependencies.py       # Annotated deps (SessionDep, CurrentUser, AdminDep)
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
| `user` | Browse products, manage own cart, place orders, cancel own pending orders, leave reviews, view own dashboard |
| `admin` | Everything + manage users, products, categories, confirm/cancel any order, full dashboard |

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
| GET | `/products/` | Any | List products (paginated, filterable by category_id) |
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
| PATCH | `/orders/{id}/cancel` | Owner | Cancel own pending order |
| PATCH | `/orders/{id}/status` | Admin | Set order status (confirmed / cancelled) |

### Dashboard
| Method | Endpoint | Auth | Description |
|---|---|---|---|
| GET | `/dashboard/transactions` | Any | Own transactions (with filters) |
| GET | `/dashboard/transactions/all` | Admin | All transactions (with filters) |
| GET | `/dashboard/summary` | Any | Own spending summary |
| GET | `/dashboard/summary/all` | Admin | Store revenue breakdown |
| GET | `/dashboard/by-category` | Any | Own category-wise totals |
| GET | `/dashboard/by-category/all` | Admin | Full category-wise totals |
| GET | `/dashboard/trends` | Any | Own monthly spending trends |
| GET | `/dashboard/trends/all` | Admin | Full monthly trends |
| GET | `/dashboard/recent` | Any | Own recent transactions |
| GET | `/dashboard/recent/all` | Admin | All recent transactions |

---

## Order Flow

```
1. User adds products to cart
2. User POST /orders/checkout → Order created (status: pending) + expense transaction recorded
3. Admin reviews pending orders via GET /orders/all
4. Admin PATCH /orders/{id}/status → {"status": "confirmed"}
5. User can cancel pending order via PATCH /orders/{id}/cancel
```

---

## Dashboard Summary

**User `GET /dashboard/summary`:**
```json
{
  "total_expense": 1500.0,
  "total_orders": 1
}
```

**Admin `GET /dashboard/summary/all`:**
```json
{
  "total_revenue": 2000.0,
  "pending_amount": 1000.0,
  "cancelled_amount": 500.0,
  "total_orders": 3
}
```

---

## Business Rules

- One review per user per product
- One product can appear once per cart
- Checkout creates an Order + expense Transaction, clears the cart
- Transactions are immutable — no update or delete
- Only pending orders can be cancelled by the user
- Deleting a category cascades to its products
- Deleting a product cascades to its reviews
- Deleting a user cascades to all their data
- Deactivated users get `403` on login

---

## Pagination

Cursor-based pagination on all list endpoints:

```bash
GET /products/                        # first page
GET /products/?cursor=42&limit=10     # next page
GET /products/?category_id=3          # filter by category
```

Response:
```json
{ "data": [...], "next_cursor": 42, "has_more": true }
```

---

## Transaction Filters

```bash
GET /dashboard/transactions?type=expense
GET /dashboard/transactions?category=order
GET /dashboard/transactions?date_from=2026-01-01&date_to=2026-03-31
```

---

## Error Handling

| Situation | Status |
|---|---|
| Duplicate name/email | `400` |
| Already reviewed | `400` |
| Empty cart checkout | `400` |
| Cancel non-pending order | `400` |
| Invalid ID | `404` |
| No permission | `403` |
| Deactivated account | `403` |
| Wrong credentials | `401` |
| DB/server error | `500` |

---

## Rate Limiting

- Global: **100 requests/minute** per IP
- `/` root: **10 requests/minute** per IP

---

## Alembic Migrations

```bash
alembic upgrade head                              # apply all
alembic revision --autogenerate -m "description" # generate new
alembic downgrade -1                              # rollback one step
alembic current                                   # check state
```

---

## First Time Setup

```
1. POST /seed-admin          → create first admin
2. POST /auth/login          → get admin JWT
3. POST /products/categories → create categories
4. POST /products/           → create products
5. POST /auth/register       → register users
6. POST /cart/               → add to cart
7. POST /orders/checkout     → place order
8. PATCH /orders/{id}/status → admin confirms
9. GET  /dashboard/summary   → view summary
```
