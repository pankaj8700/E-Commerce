from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, Depends, HTTPException
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
from sqlmodel.ext.asyncio.session import AsyncSession

from core.db import get_session
from core.exceptions import internal_error_handler
from routers import auth, users, products, reviews
from routers import cart, orders, dashboard
from schemas.user import CreateAdminRequest, UserResponse

limiter = Limiter(key_func=get_remote_address, default_limits=["100/minute"])


@asynccontextmanager
async def lifespan(app: FastAPI):
    import subprocess
    result = subprocess.run(["alembic", "upgrade", "head"], capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(f"Migration failed: {result.stderr}")
    yield


app = FastAPI(title="E-Commerce API", lifespan=lifespan)

# Rate limiting
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
app.add_exception_handler(Exception, internal_error_handler)
app.add_middleware(SlowAPIMiddleware)

# Routers
app.include_router(auth.router)
app.include_router(users.router)
app.include_router(products.router)
app.include_router(reviews.router)
app.include_router(cart.router)
app.include_router(orders.router)
app.include_router(dashboard.router)


@app.get("/")
@limiter.limit("10/minute")
async def root(request: Request):
    return {"message": "E-Commerce API is running"}


@app.post("/seed-admin", tags=["admin-bootstrap"], status_code=201, response_model=UserResponse)
async def seed_admin(body: CreateAdminRequest, session: AsyncSession = Depends(get_session)):
    """
    One-time endpoint to create the first admin user.
    Returns 409 if an admin already exists.
    Remove or disable this route in production after first use.
    """
    try:
        from crud.user import create_user, get_user_by_username, get_user_by_email
        from sqlmodel import select
        from model.user import User

        result = await session.exec(select(User).where(User.role == "admin"))
        if result.first():
            raise HTTPException(status_code=409, detail="An admin already exists. Use /auth/register-admin instead.")

        if await get_user_by_username(session, body.username):
            raise HTTPException(status_code=400, detail="Username already taken")
        if await get_user_by_email(session, body.email):
            raise HTTPException(status_code=400, detail="Email already registered")

        user = await create_user(session, body.username, body.email, body.password, role="admin")
        return user
    except HTTPException:
        raise
    except RuntimeError as e:
        raise HTTPException(status_code=500, detail=str(e))
