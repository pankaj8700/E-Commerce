from fastapi import APIRouter, HTTPException, Query
from core.dependencies import SessionDep, CurrentUser
from crud.review import get_reviews_by_product, get_review_by_id, get_review_by_user_and_product, create_review, delete_review
from crud.product import get_product_by_id
from schemas.review import ReviewCreate, ReviewResponse

router = APIRouter(prefix="/reviews", tags=["reviews"])


@router.get("/product/{product_id}", response_model=list[ReviewResponse])
async def list_reviews(
    product_id: int,
    session: SessionDep,
    _: CurrentUser,
    cursor: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
):
    try:
        items, next_cursor = await get_reviews_by_product(session, product_id, cursor=cursor, limit=limit)
        return items
    except RuntimeError as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/", status_code=201, response_model=ReviewResponse)
async def add_review(body: ReviewCreate, session: SessionDep, current_user: CurrentUser):
    try:
        product = await get_product_by_id(session, body.product_id)
        if not product:
            raise HTTPException(status_code=404, detail="Product not found. Cannot add a review for a non-existent product.")
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
async def remove_review(review_id: int, session: SessionDep, current_user: CurrentUser):
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
