from datetime import datetime
from sqlmodel import select, func
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy.exc import SQLAlchemyError
from model.order import Transaction, Order


async def get_transactions(
    session: AsyncSession,
    user_id: int,
    cursor: int = 0,
    limit: int = 10,
    type: str | None = None,
    category: str | None = None,
    date_from: datetime | None = None,
    date_to: datetime | None = None,
) -> tuple[list[Transaction], int | None]:
    try:
        query = select(Transaction).where(Transaction.user_id == user_id, Transaction.id > cursor)
        if type:
            query = query.where(Transaction.type == type)
        if category:
            query = query.where(Transaction.category == category)
        if date_from:
            query = query.where(Transaction.date >= date_from)
        if date_to:
            query = query.where(Transaction.date <= date_to)
        query = query.order_by(Transaction.id).limit(limit)
        result = await session.exec(query)
        items = result.all()
        next_cursor = items[-1].id if len(items) == limit else None
        return items, next_cursor
    except SQLAlchemyError as e:
        raise RuntimeError("Failed to fetch transactions. Please try again.") from e


async def get_all_transactions(
    session: AsyncSession,
    cursor: int = 0,
    limit: int = 10,
    type: str | None = None,
    category: str | None = None,
    date_from: datetime | None = None,
    date_to: datetime | None = None,
) -> tuple[list[Transaction], int | None]:
    try:
        query = select(Transaction).where(Transaction.id > cursor)
        if type:
            query = query.where(Transaction.type == type)
        if category:
            query = query.where(Transaction.category == category)
        if date_from:
            query = query.where(Transaction.date >= date_from)
        if date_to:
            query = query.where(Transaction.date <= date_to)
        query = query.order_by(Transaction.id).limit(limit)
        result = await session.exec(query)
        items = result.all()
        next_cursor = items[-1].id if len(items) == limit else None
        return items, next_cursor
    except SQLAlchemyError as e:
        raise RuntimeError("Failed to fetch transactions. Please try again.") from e


async def get_dashboard_summary(session: AsyncSession, user_id: int | None = None) -> dict:
    try:
        if user_id:
            # user — their total spending
            expense_q = select(func.coalesce(func.sum(Transaction.amount), 0.0)).where(
                Transaction.user_id == user_id,
                Transaction.type == "expense",
            )
            count_q = select(func.count(Transaction.id)).where(Transaction.user_id == user_id)
            expense = float((await session.exec(expense_q)).one())
            total = (await session.exec(count_q)).one()
            return {
                "total_expense": expense,
                "total_orders": total,
            }
        else:
            # admin — order breakdown by status
            def order_sum(status):
                return select(func.coalesce(func.sum(Order.total_amount), 0.0)).where(
                    Order.status == status
                )
            def order_count(status):
                return select(func.count(Order.id)).where(Order.status == status)

            total_orders_q = select(func.count(Order.id))

            revenue = float((await session.exec(order_sum("confirmed"))).one())
            pending = float((await session.exec(order_sum("pending"))).one())
            cancelled = float((await session.exec(order_sum("cancelled"))).one())
            total = (await session.exec(total_orders_q)).one()

            return {
                "total_revenue": revenue,
                "pending_amount": pending,
                "cancelled_amount": cancelled,
                "total_orders": total,
            }
    except SQLAlchemyError as e:
        raise RuntimeError("Failed to fetch dashboard summary. Please try again.") from e


async def get_category_summary(session: AsyncSession, user_id: int | None = None) -> dict:
    """Uses SQL GROUP BY — DB aggregates, not Python."""
    try:
        query = select(
            Transaction.category,
            Transaction.type,
            func.sum(Transaction.amount).label("total"),
        ).group_by(Transaction.category, Transaction.type)
        if user_id:
            query = query.where(Transaction.user_id == user_id)
        result = await session.exec(query)
        rows = result.all()
        summary: dict = {}
        for category, type_, total in rows:
            if category not in summary:
                summary[category] = {"expense": 0.0}
            summary[category][type_] = float(total)
        return summary
    except SQLAlchemyError as e:
        raise RuntimeError("Failed to fetch category summary. Please try again.") from e


async def get_recent_activity(
    session: AsyncSession, user_id: int | None = None, limit: int = 10
) -> list[Transaction]:
    try:
        query = select(Transaction)
        if user_id:
            query = query.where(Transaction.user_id == user_id)
        query = query.order_by(Transaction.date.desc()).limit(limit)
        result = await session.exec(query)
        return result.all()
    except SQLAlchemyError as e:
        raise RuntimeError("Failed to fetch recent activity. Please try again.") from e


async def get_monthly_trends(session: AsyncSession, user_id: int | None = None) -> dict:
    """Uses SQL GROUP BY strftime — DB groups by month, not Python."""
    try:
        query = select(
            func.strftime("%Y-%m", Transaction.date).label("month"),
            Transaction.type,
            func.sum(Transaction.amount).label("total"),
        ).group_by("month", Transaction.type)
        if user_id:
            query = query.where(Transaction.user_id == user_id)
        query = query.order_by("month")
        result = await session.exec(query)
        rows = result.all()
        trends: dict = {}
        for month, type_, total in rows:
            if month not in trends:
                trends[month] = {"expense": 0.0}
            trends[month][type_] = float(total)
        return trends
    except SQLAlchemyError as e:
        raise RuntimeError("Failed to fetch trends. Please try again.") from e
