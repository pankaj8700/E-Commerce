from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Query
from core.dependencies import SessionDep, CurrentUser
from core.security import require_role
from crud.transaction import (
    get_transactions, get_all_transactions,
    get_dashboard_summary, get_category_summary, get_monthly_trends,
    get_recent_activity,
)
from schemas.transaction import TransactionResponse, DashboardSummary

router = APIRouter(prefix="/dashboard", tags=["dashboard"])


@router.get("/transactions", response_model=list[TransactionResponse])
async def my_transactions(
    session: SessionDep,
    current_user: CurrentUser,
    cursor: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    type: str | None = Query(None),
    category: str | None = Query(None),
    date_from: datetime | None = Query(None),
    date_to: datetime | None = Query(None),
):
    try:
        items, _ = await get_transactions(
            session, current_user.id, cursor=cursor, limit=limit,
            type=type, category=category, date_from=date_from, date_to=date_to,
        )
        return items
    except RuntimeError as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/transactions/all", response_model=list[TransactionResponse], dependencies=[Depends(require_role("admin"))])
async def all_transactions(
    session: SessionDep,
    cursor: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    type: str | None = Query(None),
    category: str | None = Query(None),
    date_from: datetime | None = Query(None),
    date_to: datetime | None = Query(None),
):
    try:
        items, _ = await get_all_transactions(
            session, cursor=cursor, limit=limit,
            type=type, category=category, date_from=date_from, date_to=date_to,
        )
        return items
    except RuntimeError as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/summary", response_model=DashboardSummary)
async def my_summary(session: SessionDep, current_user: CurrentUser):
    try:
        return await get_dashboard_summary(session, user_id=current_user.id)
    except RuntimeError as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/summary/all", response_model=DashboardSummary, dependencies=[Depends(require_role("admin"))])
async def full_summary(session: SessionDep):
    try:
        return await get_dashboard_summary(session, user_id=None)
    except RuntimeError as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/by-category")
async def my_category_summary(session: SessionDep, current_user: CurrentUser):
    try:
        return await get_category_summary(session, user_id=current_user.id)
    except RuntimeError as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/by-category/all", dependencies=[Depends(require_role("admin"))])
async def full_category_summary(session: SessionDep):
    try:
        return await get_category_summary(session, user_id=None)
    except RuntimeError as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/trends")
async def my_trends(session: SessionDep, current_user: CurrentUser):
    try:
        return await get_monthly_trends(session, user_id=current_user.id)
    except RuntimeError as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/trends/all", dependencies=[Depends(require_role("admin"))])
async def full_trends(session: SessionDep):
    try:
        return await get_monthly_trends(session, user_id=None)
    except RuntimeError as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/recent", response_model=list[TransactionResponse])
async def my_recent_activity(
    session: SessionDep,
    current_user: CurrentUser,
    limit: int = Query(10, ge=1, le=50),
):
    try:
        return await get_recent_activity(session, user_id=current_user.id, limit=limit)
    except RuntimeError as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/recent/all", response_model=list[TransactionResponse], dependencies=[Depends(require_role("admin"))])
async def all_recent_activity(
    session: SessionDep,
    limit: int = Query(10, ge=1, le=50),
):
    try:
        return await get_recent_activity(session, user_id=None, limit=limit)
    except RuntimeError as e:
        raise HTTPException(status_code=500, detail=str(e))
