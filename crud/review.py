from typing import Optional, List, Tuple
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from core.exceptions import parse_integrity_error
from model.models import Review


async def get_reviews_by_product(
    session: AsyncSession, product_id: int, cursor: int = 0, limit: int = 10
) -> Tuple[List[Review], Optional[int]]:
    try:
        result = await session.exec(
            select(Review)
            .where(Review.product_id == product_id, Review.id > cursor)
            .order_by(Review.id)
            .limit(limit)
        )
        items = result.all()
        next_cursor = items[-1].id if len(items) == limit else None
        return items, next_cursor
    except SQLAlchemyError as e:
        raise RuntimeError("Failed to fetch reviews. Please try again.") from e


async def get_review_by_id(session: AsyncSession, review_id: int) -> Optional[Review]:
    try:
        return await session.get(Review, review_id)
    except SQLAlchemyError as e:
        raise RuntimeError("Failed to fetch review. Please try again.") from e


async def get_review_by_user_and_product(session: AsyncSession, user_id: int, product_id: int) -> Optional[Review]:
    try:
        result = await session.exec(
            select(Review).where(Review.user_id == user_id, Review.product_id == product_id)
        )
        return result.first()
    except SQLAlchemyError as e:
        raise RuntimeError("Failed to fetch review. Please try again.") from e


async def create_review(
    session: AsyncSession, text: str, rating: int, user_id: int, product_id: int
) -> Review:
    try:
        review = Review(text=text, rating=rating, user_id=user_id, product_id=product_id)
        session.add(review)
        await session.commit()
        await session.refresh(review)
        return review
    except IntegrityError as e:
        await session.rollback()
        raise ValueError(parse_integrity_error(e)) from e
    except SQLAlchemyError as e:
        await session.rollback()
        raise RuntimeError("Failed to create review. Please try again.") from e


async def delete_review(session: AsyncSession, review_id: int) -> bool:
    try:
        review = await session.get(Review, review_id)
        if not review:
            return False
        await session.delete(review)
        await session.commit()
        return True
    except SQLAlchemyError as e:
        await session.rollback()
        raise RuntimeError("Failed to delete review. Please try again.") from e
