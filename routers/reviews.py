from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel.ext.asyncio.session import AsyncSession
from core.db import get_session
from core.security import get_current_user
from crud.review import get_reviews_by_product, get_review_by_id, get_review_by_user_and_product, create_review, delete_review
from crud.product import get_product_by_id
from schemas.review import ReviewCreate

router = APIRouter(prefix="/reviews", tags=["reviews"])


@router.get("/product/{product_id}")
async def list_reviews(
    product_id: int,
    cursor: int = Query(0, ge=0, description="Last seen review ID, 0 for first page"),
    limit: int = Query(10, ge=1, le=100),
    session: AsyncSession = Depends(get_session),
    _=Depends(get_current_user),
):
    try:
        items, next_cursor = await get_reviews_by_product(session, product_id, cursor=cursor, limit=limit)
        return {"data": items, "next_cursor": next_cursor, "has_more": next_cursor is not None}
    except RuntimeError as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/", status_code=201)
async def add_review(
    body: ReviewCreate,
    session: AsyncSession = Depends(get_session),
    current_user=Depends(get_current_user),
):
    try:
        product = await get_product_by_id(session, body.product_id)
        if not product:
            raise HTTPException(status_code=404, detail="Product not found. Cannot add a review for a non-existent product.")
        # check if user already reviewed this product
        existing = await get_review_by_user_and_product(session, current_user.id, body.product_id)
        if existing:
            raise HTTPException(status_code=400, detail="You have already reviewed this product.")
        return await create_review(session, body.text, body.rating, current_user.id, body.product_id)
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except RuntimeError as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{review_id}")
async def remove_review(
    review_id: int,
    session: AsyncSession = Depends(get_session),
    current_user=Depends(get_current_user),
):
    try:
        review = await get_review_by_id(session, review_id)
        if not review:
            raise HTTPException(status_code=404, detail="Review not found.")
        if review.user_id != current_user.id and current_user.role != "admin":
            raise HTTPException(status_code=403, detail="You are not allowed to delete this review.")
        await delete_review(session, review_id)
        return {"detail": "Review deleted successfully."}
    except HTTPException:
        raise
    except RuntimeError as e:
        raise HTTPException(status_code=500, detail=str(e))
