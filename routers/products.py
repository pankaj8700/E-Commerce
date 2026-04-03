from fastapi import APIRouter, Depends, HTTPException, Query
from core.dependencies import SessionDep, CurrentUser
from core.security import require_role
from crud.product import (
    get_all_products, get_product_by_id,
    create_product, update_product, delete_product,
    get_all_categories, create_category, get_category_by_id, delete_category,
)
from schemas.product import ProductCreate, ProductUpdate, CategoryCreate, ProductResponse, CategoryResponse

router = APIRouter(prefix="/products", tags=["products"])


@router.get("/categories", response_model=list[CategoryResponse])
async def list_categories(
    session: SessionDep,
    _: CurrentUser,
    cursor: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
):
    try:
        items, next_cursor = await get_all_categories(session, cursor=cursor, limit=limit)
        return items
    except RuntimeError as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/categories", status_code=201, response_model=CategoryResponse, dependencies=[Depends(require_role("admin"))])
async def add_category(body: CategoryCreate, session: SessionDep):
    try:
        return await create_category(session, body.name)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except RuntimeError as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/categories/{category_id}", dependencies=[Depends(require_role("admin"))])
async def remove_category(category_id: int, session: SessionDep):
    try:
        deleted = await delete_category(session, category_id)
        if not deleted:
            raise HTTPException(status_code=404, detail="Category not found.")
        return {"detail": "Category deleted successfully."}
    except HTTPException:
        raise
    except RuntimeError as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/", response_model=list[ProductResponse])
async def list_products(
    session: SessionDep,
    _: CurrentUser,
    cursor: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    category_id: int | None = Query(None, gt=0),
):
    try:
        items, next_cursor = await get_all_products(session, cursor=cursor, limit=limit, category_id=category_id)
        return items
    except RuntimeError as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{product_id}", response_model=ProductResponse)
async def get_product(product_id: int, session: SessionDep, _: CurrentUser):
    try:
        product = await get_product_by_id(session, product_id)
        if not product:
            raise HTTPException(status_code=404, detail="Product not found.")
        return product
    except HTTPException:
        raise
    except RuntimeError as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/", status_code=201, response_model=ProductResponse, dependencies=[Depends(require_role("admin"))])
async def add_product(body: ProductCreate, session: SessionDep):
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


@router.patch("/{product_id}", response_model=ProductResponse, dependencies=[Depends(require_role("admin"))])
async def edit_product(product_id: int, body: ProductUpdate, session: SessionDep):
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
async def remove_product(product_id: int, session: SessionDep):
    try:
        deleted = await delete_product(session, product_id)
        if not deleted:
            raise HTTPException(status_code=404, detail="Product not found.")
        return {"detail": "Product deleted successfully."}
    except HTTPException:
        raise
    except RuntimeError as e:
        raise HTTPException(status_code=500, detail=str(e))
