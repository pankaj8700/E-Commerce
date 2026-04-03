
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy.exc import SQLAlchemyError
from model.order import Order, OrderItem, Transaction
from model.cart import CartItem
from model.product import Product


async def checkout(session: AsyncSession, user_id: int) -> Order:
    try:
        # fetch cart items
        result = await session.exec(select(CartItem).where(CartItem.user_id == user_id))
        cart_items = result.all()
        if not cart_items:
            raise ValueError("Your cart is empty.")

        # build order
        total = 0.0
        order = Order(user_id=user_id, total_amount=0.0)
        session.add(order)
        await session.flush()  # get order.id without committing

        order_items = []
        for item in cart_items:
            product = await session.get(Product, item.product_id)
            if not product:
                raise ValueError(f"Product ID {item.product_id} no longer exists.")
            subtotal = product.price * item.quantity
            total += subtotal
            order_items.append(OrderItem(
                order_id=order.id,
                product_id=item.product_id,
                quantity=item.quantity,
                price_at_purchase=product.price,
            ))

        # update total
        order.total_amount = total
        session.add(order)

        # save order items
        for oi in order_items:
            session.add(oi)

        # create transaction
        transaction = Transaction(
            amount=total,
            type="expense",
            category="order",
            user_id=user_id,
            order_id=order.id,
            notes=f"Order #{order.id}",
        )
        session.add(transaction)

        # clear cart
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


async def get_order_items(session: AsyncSession, order_id: int) -> list[OrderItem]:
    try:
        result = await session.exec(select(OrderItem).where(OrderItem.order_id == order_id))
        return result.all()
    except SQLAlchemyError as e:
        raise RuntimeError("Failed to fetch order items. Please try again.") from e
