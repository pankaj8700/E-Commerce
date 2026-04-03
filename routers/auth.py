from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from core.dependencies import SessionDep
from core.security import verify_password, create_access_token, require_role
from crud.user import get_user_by_username, get_user_by_email, create_user
from schemas.user import RegisterRequest, CreateAdminRequest, UserResponse, TokenResponse

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", status_code=201, response_model=UserResponse)
async def register(body: RegisterRequest, session: SessionDep):
    try:
        if await get_user_by_username(session, body.username):
            raise HTTPException(status_code=400, detail="This username is already taken. Please choose another.")
        if await get_user_by_email(session, body.email):
            raise HTTPException(status_code=400, detail="An account with this email already exists.")
        return await create_user(session, body.username, body.email, body.password, role="user")
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except RuntimeError as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/register-admin", status_code=201, response_model=UserResponse, dependencies=[Depends(require_role("admin"))])
async def register_admin(body: CreateAdminRequest, session: SessionDep):
    try:
        if await get_user_by_username(session, body.username):
            raise HTTPException(status_code=400, detail="This username is already taken. Please choose another.")
        if await get_user_by_email(session, body.email):
            raise HTTPException(status_code=400, detail="An account with this email already exists.")
        return await create_user(session, body.username, body.email, body.password, role="admin")
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except RuntimeError as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/login", response_model=TokenResponse)
async def login(session: SessionDep, form: OAuth2PasswordRequestForm = Depends()):
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
