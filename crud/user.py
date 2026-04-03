
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from core.exceptions import parse_integrity_error
from model.user import User
from model.enums import Role
from core.security import hash_password


async def get_user_by_username(session: AsyncSession, username: str) -> User | None:
    try:
        result = await session.exec(select(User).where(User.username == username))
        return result.first()
    except SQLAlchemyError as e:
        raise RuntimeError("Failed to fetch user. Please try again.") from e


async def get_user_by_email(session: AsyncSession, email: str) -> User | None:
    try:
        result = await session.exec(select(User).where(User.email == email))
        return result.first()
    except SQLAlchemyError as e:
        raise RuntimeError("Failed to fetch user. Please try again.") from e


async def get_user_by_id(session: AsyncSession, user_id: int) -> User | None:
    try:
        return await session.get(User, user_id)
    except SQLAlchemyError as e:
        raise RuntimeError("Failed to fetch user. Please try again.") from e


async def get_all_users(
    session: AsyncSession, cursor: int = 0, limit: int = 10
) -> tuple[list[User], int | None]:
    try:
        result = await session.exec(
            select(User).where(User.id > cursor).order_by(User.id).limit(limit)
        )
        items = result.all()
        next_cursor = items[-1].id if len(items) == limit else None
        return items, next_cursor
    except SQLAlchemyError as e:
        raise RuntimeError("Failed to fetch users. Please try again.") from e


async def create_user(
    session: AsyncSession, username: str, email: str, password: str, role: str = "user"
) -> User:
    try:
        role_value = role.value if isinstance(role, Role) else role
        user = User(username=username, email=email, password=hash_password(password), role=role_value)
        session.add(user)
        await session.commit()
        await session.refresh(user)
        return user
    except IntegrityError as e:
        await session.rollback()
        raise ValueError(parse_integrity_error(e)) from e
    except SQLAlchemyError as e:
        await session.rollback()
        raise RuntimeError("Failed to create user. Please try again.") from e


async def delete_user(session: AsyncSession, user_id: int) -> bool:
    try:
        user = await session.get(User, user_id)
        if not user:
            return False
        await session.delete(user)
        await session.commit()
        return True
    except SQLAlchemyError as e:
        await session.rollback()
        raise RuntimeError("Failed to delete user. Please try again.") from e


async def promote_to_admin(session: AsyncSession, user_id: int) -> User | None:
    try:
        user = await session.get(User, user_id)
        if not user:
            return None
        user.role = Role.admin.value
        session.add(user)
        await session.commit()
        await session.refresh(user)
        return user
    except SQLAlchemyError as e:
        await session.rollback()
        raise RuntimeError("Failed to promote user. Please try again.") from e


async def toggle_active(session: AsyncSession, user_id: int) -> User | None:
    try:
        user = await session.get(User, user_id)
        if not user:
            return None
        user.is_active = not user.is_active
        session.add(user)
        await session.commit()
        await session.refresh(user)
        return user
    except SQLAlchemyError as e:
        await session.rollback()
        raise RuntimeError("Failed to update user status. Please try again.") from e
