from typing import Optional, List, Tuple
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from core.exceptions import parse_integrity_error
from model.models import Product, Category


async def get_all_products(
    session: AsyncSession, cursor: int = 0, limit: int = 10
) -> Tuple[List[Product], Optional[int]]:
    try:
        result = await session.exec(
            select(Product).where(Product.id > cursor).order_by(Product.id).limit(limit)
        )
        items = result.all()
        next_cursor = items[-1].id if len(items) == limit else None
        return items, next_cursor
    except SQLAlchemyError as e:
        raise RuntimeError("Failed to fetch products. Please try again.") from e


async def get_product_by_id(session: AsyncSession, product_id: int) -> Optional[Product]:
    try:
        return await session.get(Product, product_id)
    except SQLAlchemyError as e:
        raise RuntimeError("Failed to fetch product. Please try again.") from e


async def create_product(
    session: AsyncSession, name: str, description: str, price: float, category_id: Optional[int]
) -> Product:
    try:
        product = Product(name=name, description=description, price=price, category_id=category_id)
        session.add(product)
        await session.commit()
        await session.refresh(product)
        return product
    except IntegrityError as e:
        await session.rollback()
        raise ValueError(parse_integrity_error(e)) from e
    except SQLAlchemyError as e:
        await session.rollback()
        raise RuntimeError("Failed to create product. Please try again.") from e


async def update_product(session: AsyncSession, product_id: int, **kwargs) -> Optional[Product]:
    try:
        product = await session.get(Product, product_id)
        if not product:
            return None
        for key, value in kwargs.items():
            setattr(product, key, value)
        session.add(product)
        await session.commit()
        await session.refresh(product)
        return product
    except IntegrityError as e:
        await session.rollback()
        raise ValueError(parse_integrity_error(e)) from e
    except SQLAlchemyError as e:
        await session.rollback()
        raise RuntimeError("Failed to update product. Please try again.") from e


async def delete_product(session: AsyncSession, product_id: int) -> bool:
    try:
        product = await session.get(Product, product_id)
        if not product:
            return False
        await session.delete(product)
        await session.commit()
        return True
    except SQLAlchemyError as e:
        await session.rollback()
        raise RuntimeError("Failed to delete product. Please try again.") from e


async def get_all_categories(
    session: AsyncSession, cursor: int = 0, limit: int = 10
) -> Tuple[List[Category], Optional[int]]:
    try:
        result = await session.exec(
            select(Category).where(Category.id > cursor).order_by(Category.id).limit(limit)
        )
        items = result.all()
        next_cursor = items[-1].id if len(items) == limit else None
        return items, next_cursor
    except SQLAlchemyError as e:
        raise RuntimeError("Failed to fetch categories. Please try again.") from e


async def create_category(session: AsyncSession, name: str) -> Category:
    try:
        category = Category(name=name)
        session.add(category)
        await session.commit()
        await session.refresh(category)
        return category
    except IntegrityError as e:
        await session.rollback()
        raise ValueError(parse_integrity_error(e)) from e
    except SQLAlchemyError as e:
        await session.rollback()
        raise RuntimeError("Failed to create category. Please try again.") from e


async def get_category_by_id(session: AsyncSession, category_id: int) -> Optional[Category]:
    try:
        return await session.get(Category, category_id)
    except SQLAlchemyError as e:
        raise RuntimeError("Failed to fetch category. Please try again.") from e


async def delete_category(session: AsyncSession, category_id: int) -> bool:
    try:
        category = await session.get(Category, category_id)
        if not category:
            return False
        await session.delete(category)
        await session.commit()
        return True
    except SQLAlchemyError as e:
        await session.rollback()
        raise RuntimeError("Failed to delete category. Please try again.") from e
