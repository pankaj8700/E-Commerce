from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel.ext.asyncio.session import AsyncSession
from core.db import get_session
from core.security import get_current_user, require_role
from crud.product import (
    get_all_products, get_product_by_id,
    create_product, update_product, delete_product,
    get_all_categories, create_category, get_category_by_id, delete_category,
)
from schemas.product import ProductCreate, ProductUpdate, CategoryCreate

router = APIRouter(prefix="/products", tags=["products"])


# --- Categories ---

@router.get("/categories")
async def list_categories(
    cursor: int = Query(0, ge=0, description="Last seen category ID, 0 for first page"),
    limit: int = Query(10, ge=1, le=100),
    session: AsyncSession = Depends(get_session),
    _=Depends(get_current_user),
):
    try:
        items, next_cursor = await get_all_categories(session, cursor=cursor, limit=limit)
        return {"data": items, "next_cursor": next_cursor, "has_more": next_cursor is not None}
    except RuntimeError as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/categories", status_code=201, dependencies=[Depends(require_role("admin"))])
async def add_category(body: CategoryCreate, session: AsyncSession = Depends(get_session)):
    try:
        return await create_category(session, body.name)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except RuntimeError as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/categories/{category_id}", dependencies=[Depends(require_role("admin"))])
async def remove_category(category_id: int, session: AsyncSession = Depends(get_session)):
    try:
        deleted = await delete_category(session, category_id)
        if not deleted:
            raise HTTPException(status_code=404, detail="Category not found.")
        return {"detail": "Category deleted successfully."}
    except HTTPException:
        raise
    except RuntimeError as e:
        raise HTTPException(status_code=500, detail=str(e))


# --- Products ---

@router.get("/")
async def list_products(
    cursor: int = Query(0, ge=0, description="Last seen product ID, 0 for first page"),
    limit: int = Query(10, ge=1, le=100),
    session: AsyncSession = Depends(get_session),
    _=Depends(get_current_user),
):
    try:
        items, next_cursor = await get_all_products(session, cursor=cursor, limit=limit)
        return {"data": items, "next_cursor": next_cursor, "has_more": next_cursor is not None}
    except RuntimeError as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{product_id}")
async def get_product(product_id: int, session: AsyncSession = Depends(get_session), _=Depends(get_current_user)):
    try:
        product = await get_product_by_id(session, product_id)
        if not product:
            raise HTTPException(status_code=404, detail="Product not found.")
        return product
    except HTTPException:
        raise
    except RuntimeError as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/", status_code=201, dependencies=[Depends(require_role("admin"))])
async def add_product(body: ProductCreate, session: AsyncSession = Depends(get_session)):
    try:
        if body.category_id is not None:
            if not await get_category_by_id(session, body.category_id):
                raise HTTPException(status_code=404, detail="Category not found.")
        return await create_product(session, body.name, body.description, body.price, body.category_id)
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except RuntimeError as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.patch("/{product_id}", dependencies=[Depends(require_role("admin"))])
async def edit_product(product_id: int, body: ProductUpdate, session: AsyncSession = Depends(get_session)):
    try:
        if body.category_id is not None:
            if not await get_category_by_id(session, body.category_id):
                raise HTTPException(status_code=404, detail="Category not found.")
        product = await update_product(session, product_id, **body.model_dump(exclude_none=True))
        if not product:
            raise HTTPException(status_code=404, detail="Product not found.")
        return product
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except RuntimeError as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{product_id}", dependencies=[Depends(require_role("admin"))])
async def remove_product(product_id: int, session: AsyncSession = Depends(get_session)):
    try:
        deleted = await delete_product(session, product_id)
        if not deleted:
            raise HTTPException(status_code=404, detail="Product not found.")
        return {"detail": "Product deleted successfully."}
    except HTTPException:
        raise
    except RuntimeError as e:
        raise HTTPException(status_code=500, detail=str(e))
