from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlmodel.ext.asyncio.session import AsyncSession
from core.db import get_session
from core.security import verify_password, create_access_token, require_role
from crud.user import get_user_by_username, get_user_by_email, create_user
from schemas.user import RegisterRequest, CreateAdminRequest

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", status_code=201)
async def register(body: RegisterRequest, session: AsyncSession = Depends(get_session)):
    try:
        if await get_user_by_username(session, body.username):
            raise HTTPException(status_code=400, detail="This username is already taken. Please choose another.")
        if await get_user_by_email(session, body.email):
            raise HTTPException(status_code=400, detail="An account with this email already exists.")
        user = await create_user(session, body.username, body.email, body.password, role="user")
        return {"id": user.id, "username": user.username, "role": user.role}
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except RuntimeError as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/register-admin", status_code=201, dependencies=[Depends(require_role("admin"))])
async def register_admin(body: CreateAdminRequest, session: AsyncSession = Depends(get_session)):
    try:
        if await get_user_by_username(session, body.username):
            raise HTTPException(status_code=400, detail="This username is already taken. Please choose another.")
        if await get_user_by_email(session, body.email):
            raise HTTPException(status_code=400, detail="An account with this email already exists.")
        user = await create_user(session, body.username, body.email, body.password, role="admin")
        return {"id": user.id, "username": user.username, "role": user.role}
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except RuntimeError as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/login")
async def login(form: OAuth2PasswordRequestForm = Depends(), session: AsyncSession = Depends(get_session)):
    try:
        user = await get_user_by_username(session, form.username)
        if not user or not verify_password(form.password, user.password):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid username or password.")
        token = create_access_token({"sub": user.username, "role": user.role})
        return {"access_token": token, "token_type": "bearer"}
    except HTTPException:
        raise
    except RuntimeError as e:
        raise HTTPException(status_code=500, detail=str(e))
