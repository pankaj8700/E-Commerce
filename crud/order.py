from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy.exc import SQLAlchemyError
from model.order import Order, OrderItem, Transaction
from model.cart import CartItem
from model.product import Product


async def checkout(session: AsyncSession, user_id: int) -> Order:
    try:
        result = await session.exec(select(CartItem).where(CartItem.user_id == user_id))
        cart_items = result.all()
        if not cart_items:
            raise ValueError("Your cart is empty.")

        # fetch all products in ONE query — no N+1
        product_ids = [item.product_id for item in cart_items]
        products_result = await session.exec(select(Product).where(Product.id.in_(product_ids)))
        products = {p.id: p for p in products_result.all()}

        missing = [pid for pid in product_ids if pid not in products]
        if missing:
            raise ValueError(f"Some products no longer exist: {missing}")

        order = Order(user_id=user_id, total_amount=0.0)
        session.add(order)
        await session.flush()

        total = 0.0
        for item in cart_items:
            product = products[item.product_id]
            subtotal = product.price * item.quantity
            total += subtotal
            session.add(OrderItem(
                order_id=order.id,
                product_id=item.product_id,
                quantity=item.quantity,
                price_at_purchase=product.price,
            ))

        order.total_amount = total
        session.add(order)

        session.add(Transaction(
            amount=total,
            type="expense",
            category="order",
            user_id=user_id,
            order_id=order.id,
            notes=f"Order #{order.id}",
        ))

        for item in cart_items:
            await session.delete(item)

        await session.commit()
        await session.refresh(order)
        return order

    except ValueError:
        await session.rollback()
        raise
    except SQLAlchemyError as e:
        await session.rollback()
        raise RuntimeError("Failed to place order. Please try again.") from e


async def get_orders(
    session: AsyncSession, user_id: int, cursor: int = 0, limit: int = 10
) -> tuple[list[Order], int | None]:
    try:
        result = await session.exec(
            select(Order)
            .where(Order.user_id == user_id, Order.id > cursor)
            .order_by(Order.id)
            .limit(limit)
        )
        items = result.all()
        next_cursor = items[-1].id if len(items) == limit else None
        return items, next_cursor
    except SQLAlchemyError as e:
        raise RuntimeError("Failed to fetch orders. Please try again.") from e


async def get_all_orders(
    session: AsyncSession, cursor: int = 0, limit: int = 10
) -> tuple[list[Order], int | None]:
    try:
        result = await session.exec(
            select(Order).where(Order.id > cursor).order_by(Order.id).limit(limit)
        )
        items = result.all()
        next_cursor = items[-1].id if len(items) == limit else None
        return items, next_cursor
    except SQLAlchemyError as e:
        raise RuntimeError("Failed to fetch orders. Please try again.") from e


async def get_order_by_id(session: AsyncSession, order_id: int) -> Order | None:
    try:
        return await session.get(Order, order_id)
    except SQLAlchemyError as e:
        raise RuntimeError("Failed to fetch order. Please try again.") from e


async def update_order_status(session: AsyncSession, order_id: int, status: str) -> Order | None:
    try:
        order = await session.get(Order, order_id)
        if not order:
            return None
        order.status = status
        session.add(order)
        await session.commit()
        await session.refresh(order)
        return order
    except SQLAlchemyError as e:
        await session.rollback()
        raise RuntimeError("Failed to update order status. Please try again.") from e


async def get_order_items(session: AsyncSession, order_id: int) -> list[OrderItem]:
    try:
        result = await session.exec(select(OrderItem).where(OrderItem.order_id == order_id))
        return result.all()
    except SQLAlchemyError as e:
        raise RuntimeError("Failed to fetch order items. Please try again.") from e
