
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from core.exceptions import parse_integrity_error
from model.cart import CartItem


async def get_cart_items(session: AsyncSession, user_id: int) -> list[CartItem]:
    try:
        result = await session.exec(select(CartItem).where(CartItem.user_id == user_id))
        return result.all()
    except SQLAlchemyError as e:
        raise RuntimeError("Failed to fetch cart. Please try again.") from e


async def get_cart_item(session: AsyncSession, user_id: int, product_id: int) -> CartItem | None:
    try:
        result = await session.exec(
            select(CartItem).where(CartItem.user_id == user_id, CartItem.product_id == product_id)
        )
        return result.first()
    except SQLAlchemyError as e:
        raise RuntimeError("Failed to fetch cart item. Please try again.") from e


async def get_cart_item_by_id(session: AsyncSession, item_id: int) -> CartItem | None:
    try:
        return await session.get(CartItem, item_id)
    except SQLAlchemyError as e:
        raise RuntimeError("Failed to fetch cart item. Please try again.") from e


async def add_to_cart(session: AsyncSession, user_id: int, product_id: int, quantity: int) -> CartItem:
    try:
        item = CartItem(user_id=user_id, product_id=product_id, quantity=quantity)
        session.add(item)
        await session.commit()
        await session.refresh(item)
        return item
    except IntegrityError as e:
        await session.rollback()
        raise ValueError(parse_integrity_error(e)) from e
    except SQLAlchemyError as e:
        await session.rollback()
        raise RuntimeError("Failed to add item to cart. Please try again.") from e


async def update_cart_item(session: AsyncSession, item_id: int, quantity: int) -> CartItem | None:
    try:
        item = await session.get(CartItem, item_id)
        if not item:
            return None
        item.quantity = quantity
        session.add(item)
        await session.commit()
        await session.refresh(item)
        return item
    except SQLAlchemyError as e:
        await session.rollback()
        raise RuntimeError("Failed to update cart item. Please try again.") from e


async def remove_cart_item(session: AsyncSession, item_id: int) -> bool:
    try:
        item = await session.get(CartItem, item_id)
        if not item:
            return False
        await session.delete(item)
        await session.commit()
        return True
    except SQLAlchemyError as e:
        await session.rollback()
        raise RuntimeError("Failed to remove cart item. Please try again.") from e


async def clear_cart(session: AsyncSession, user_id: int) -> None:
    try:
        result = await session.exec(select(CartItem).where(CartItem.user_id == user_id))
        for item in result.all():
            await session.delete(item)
        await session.commit()
    except SQLAlchemyError as e:
        await session.rollback()
        raise RuntimeError("Failed to clear cart. Please try again.") from e
