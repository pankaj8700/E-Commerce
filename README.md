# E-Commerce API

A FastAPI-based REST API with JWT authentication, RBAC, cursor-based pagination, rate limiting, and Alembic migrations.

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
├── alembic/               # migration files
│   └── versions/
├── core/
│   ├── config.py          # settings (DATABASE_URL, SECRET_KEY, etc.)
│   ├── db.py              # async engine & session
│   ├── security.py        # JWT, password hashing, RBAC
│   └── exceptions.py      # global error handler + integrity error parser
├── crud/
│   ├── user.py
│   ├── product.py
│   └── review.py
├── model/
│   └── models.py          # SQLModel table definitions
├── routers/
│   ├── auth.py
│   ├── users.py
│   ├── products.py
│   └── reviews.py
├── schemas/
│   ├── user.py
│   ├── product.py
│   └── review.py
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
| `user` | Browse products & categories, create/delete own reviews |
| `admin` | Everything + manage users, products, categories, any review |

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

---

## Business Rules

- A user can only submit **one review per product** — duplicate attempts return `400`
- Deleting a category also deletes all its products (CASCADE)
- Deleting a product also deletes all its reviews (CASCADE)
- Deleting a user also deletes all their reviews (CASCADE)
- Only the review owner or an admin can delete a review
- `category_id` must be a valid existing category ID (checked before insert)

---

## Pagination

All list endpoints use **cursor-based pagination** — stable even when new records are added or deleted.

```bash
# First page
GET /products/

# Next page — pass next_cursor from previous response
GET /products/?cursor=42&limit=10
```

Response format:
```json
{
  "data": [...],
  "next_cursor": 42,
  "has_more": true
}
```

`has_more: false` means no more records.

---

## Error Handling

All errors return human-readable messages:

| Situation | Status | Example message |
|---|---|---|
| Duplicate name/email | `400` | "A record with this name already exists." |
| Already reviewed | `400` | "You have already reviewed this product." |
| Invalid ID | `404` | "Product not found." |
| No permission | `403` | "You are not allowed to delete this review." |
| Wrong credentials | `401` | "Invalid username or password." |
| DB/server error | `500` | "Failed to create product. Please try again." |

---

## Rate Limiting

- Global: **100 requests/minute** per IP
- `/` root: **10 requests/minute** per IP

Returns `429 Too Many Requests` when exceeded.

---

## Alembic Migrations

```bash
# Apply all pending migrations
alembic upgrade head

# Generate new migration after model changes
alembic revision --autogenerate -m "your_change_description"

# Rollback one step
alembic downgrade -1

# Check current state
alembic current

# View migration history
alembic history
```

---

## First Time Setup Flow

```
1. POST /seed-admin                → create first admin (no auth needed)
2. POST /auth/login                → get admin JWT
3. POST /products/categories       → create categories (admin JWT)
4. POST /products/                 → create products (admin JWT)
5. POST /auth/register             → register normal users
6. POST /reviews/                  → users leave reviews on products
```
