from fastapi import APIRouter, Depends, HTTPException, Query
from core.dependencies import SessionDep, CurrentUser
from core.security import require_role
from crud.order import checkout, get_orders, get_all_orders, get_order_by_id, get_order_items
from schemas.order import OrderResponse, OrderDetailResponse, OrderItemResponse

router = APIRouter(prefix="/orders", tags=["orders"])


@router.post("/checkout", status_code=201, response_model=OrderResponse)
async def place_order(session: SessionDep, current_user: CurrentUser):
    try:
        return await checkout(session, current_user.id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except RuntimeError as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/", response_model=list[OrderResponse])
async def list_my_orders(
    session: SessionDep,
    current_user: CurrentUser,
    cursor: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
):
    try:
        items, next_cursor = await get_orders(session, current_user.id, cursor=cursor, limit=limit)
        return items
    except RuntimeError as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/all", response_model=list[OrderResponse], dependencies=[Depends(require_role("admin"))])
async def list_all_orders(
    session: SessionDep,
    cursor: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
):
    try:
        items, next_cursor = await get_all_orders(session, cursor=cursor, limit=limit)
        return items
    except RuntimeError as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{order_id}", response_model=OrderDetailResponse)
async def order_detail(order_id: int, session: SessionDep, current_user: CurrentUser):
    try:
        order = await get_order_by_id(session, order_id)
        if not order:
            raise HTTPException(status_code=404, detail="Order not found.")
        if order.user_id != current_user.id and current_user.role != "admin":
            raise HTTPException(status_code=403, detail="Not allowed.")
        items = await get_order_items(session, order_id)
        return {"order": order, "items": items}
    except HTTPException:
        raise
    except RuntimeError as e:
        raise HTTPException(status_code=500, detail=str(e))
