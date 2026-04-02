from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel.ext.asyncio.session import AsyncSession
from core.db import get_session
from core.security import get_current_user, require_role
from crud.user import get_all_users, delete_user, promote_to_admin

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/me")
async def me(current_user=Depends(get_current_user)):
    return {"id": current_user.id, "username": current_user.username, "email": current_user.email, "role": current_user.role}


@router.get("/", dependencies=[Depends(require_role("admin"))])
async def list_users(
    cursor: int = Query(0, ge=0, description="Last seen user ID, 0 for first page"),
    limit: int = Query(10, ge=1, le=100),
    session: AsyncSession = Depends(get_session),
):
    try:
        items, next_cursor = await get_all_users(session, cursor=cursor, limit=limit)
        return {"data": items, "next_cursor": next_cursor, "has_more": next_cursor is not None}
    except RuntimeError as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.patch("/{user_id}/promote", dependencies=[Depends(require_role("admin"))])
async def promote_user(user_id: int, session: AsyncSession = Depends(get_session)):
    try:
        user = await promote_to_admin(session, user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found.")
        return {"id": user.id, "username": user.username, "role": user.role}
    except HTTPException:
        raise
    except RuntimeError as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{user_id}", dependencies=[Depends(require_role("admin"))])
async def remove_user(user_id: int, session: AsyncSession = Depends(get_session)):
    try:
        deleted = await delete_user(session, user_id)
        if not deleted:
            raise HTTPException(status_code=404, detail="User not found.")
        return {"detail": "User deleted successfully."}
    except HTTPException:
        raise
    except RuntimeError as e:
        raise HTTPException(status_code=500, detail=str(e))
