from fastapi import APIRouter, HTTPException
from core.dependencies import SessionDep, CurrentUser
from crud.cart import get_cart_items, get_cart_item, get_cart_item_by_id, add_to_cart, update_cart_item, remove_cart_item
from crud.product import get_product_by_id
from schemas.cart import CartItemAdd, CartItemUpdate, CartItemResponse

router = APIRouter(prefix="/cart", tags=["cart"])


@router.get("/", response_model=list[CartItemResponse])
async def view_cart(session: SessionDep, current_user: CurrentUser):
    try:
        return await get_cart_items(session, current_user.id)
    except RuntimeError as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/", status_code=201, response_model=CartItemResponse)
async def add_item(body: CartItemAdd, session: SessionDep, current_user: CurrentUser):
    try:
        product = await get_product_by_id(session, body.product_id)
        if not product:
            raise HTTPException(status_code=404, detail="Product not found.")
        existing = await get_cart_item(session, current_user.id, body.product_id)
        if existing:
            raise HTTPException(status_code=400, detail="Product already in cart. Use PATCH to update quantity.")
        return await add_to_cart(session, current_user.id, body.product_id, body.quantity)
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except RuntimeError as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.patch("/{item_id}", response_model=CartItemResponse)
async def update_item(item_id: int, body: CartItemUpdate, session: SessionDep, current_user: CurrentUser):
    try:
        item = await get_cart_item_by_id(session, item_id)
        if not item or item.user_id != current_user.id:
            raise HTTPException(status_code=404, detail="Cart item not found.")
        return await update_cart_item(session, item_id, body.quantity)
    except HTTPException:
        raise
    except RuntimeError as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{item_id}")
async def remove_item(item_id: int, session: SessionDep, current_user: CurrentUser):
    try:
        item = await get_cart_item_by_id(session, item_id)
        if not item or item.user_id != current_user.id:
            raise HTTPException(status_code=404, detail="Cart item not found.")
        await remove_cart_item(session, item_id)
        return {"detail": "Item removed from cart."}
    except HTTPException:
        raise
    except RuntimeError as e:
        raise HTTPException(status_code=500, detail=str(e))
