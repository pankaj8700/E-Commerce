
from datetime import datetime
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy.exc import SQLAlchemyError
from model.order import Transaction


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
        query = select(Transaction)
        if user_id:
            query = query.where(Transaction.user_id == user_id)
        result = await session.exec(query)
        transactions = result.all()

        total_income = sum(t.amount for t in transactions if t.type == "income")
        total_expense = sum(t.amount for t in transactions if t.type == "expense")

        return {
            "total_income": total_income,
            "total_expense": total_expense,
            "net_balance": total_income - total_expense,
            "total_transactions": len(transactions),
        }
    except SQLAlchemyError as e:
        raise RuntimeError("Failed to fetch dashboard summary. Please try again.") from e


async def get_category_summary(session: AsyncSession, user_id: int | None = None) -> dict:
    try:
        query = select(Transaction)
        if user_id:
            query = query.where(Transaction.user_id == user_id)
        result = await session.exec(query)
        transactions = result.all()

        summary = {}
        for t in transactions:
            if t.category not in summary:
                summary[t.category] = {"income": 0.0, "expense": 0.0}
            summary[t.category][t.type] += t.amount
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
    try:
        query = select(Transaction)
        if user_id:
            query = query.where(Transaction.user_id == user_id)
        result = await session.exec(query)
        transactions = result.all()

        trends = {}
        for t in transactions:
            key = t.date.strftime("%Y-%m")
            if key not in trends:
                trends[key] = {"income": 0.0, "expense": 0.0}
            trends[key][t.type] += t.amount

        # sort by month
        return dict(sorted(trends.items()))
    except SQLAlchemyError as e:
        raise RuntimeError("Failed to fetch trends. Please try again.") from e
