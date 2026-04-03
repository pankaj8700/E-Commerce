from fastapi import APIRouter, Depends, HTTPException, Query
from core.dependencies import SessionDep, CurrentUser
from core.security import require_role
from crud.user import get_all_users, delete_user, promote_to_admin, toggle_active
from schemas.user import UserResponse

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/me", response_model=UserResponse)
async def me(current_user: CurrentUser):
    return current_user


@router.get("/", response_model=list[UserResponse], dependencies=[Depends(require_role("admin"))])
async def list_users(
    session: SessionDep,
    cursor: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
):
    try:
        items, next_cursor = await get_all_users(session, cursor=cursor, limit=limit)
        return items
    except RuntimeError as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.patch("/{user_id}/promote", response_model=UserResponse, dependencies=[Depends(require_role("admin"))])
async def promote_user(user_id: int, session: SessionDep):
    try:
        user = await promote_to_admin(session, user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found.")
        return user
    except HTTPException:
        raise
    except RuntimeError as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.patch("/{user_id}/toggle-active", response_model=UserResponse, dependencies=[Depends(require_role("admin"))])
async def toggle_user_active(user_id: int, session: SessionDep):
    try:
        user = await toggle_active(session, user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found.")
        return user
    except HTTPException:
        raise
    except RuntimeError as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{user_id}", dependencies=[Depends(require_role("admin"))])
async def remove_user(user_id: int, session: SessionDep):
    try:
        deleted = await delete_user(session, user_id)
        if not deleted:
            raise HTTPException(status_code=404, detail="User not found.")
        return {"detail": "User deleted successfully."}
    except HTTPException:
        raise
    except RuntimeError as e:
        raise HTTPException(status_code=500, detail=str(e))
