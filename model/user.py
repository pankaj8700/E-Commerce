from typing import TYPE_CHECKING
from sqlmodel import Field, SQLModel, Relationship

if TYPE_CHECKING:
    from model.order import Order, Transaction
    from model.cart import CartItem
    from model.product import Review


class User(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    username: str = Field(max_length=20, unique=True, index=True)
    email: str = Field(unique=True, index=True)
    password: str = Field(max_length=128)
    role: str = Field(default="user")
    is_active: bool = Field(default=True)

    reviews: list["Review"] = Relationship(
        back_populates="user",
        sa_relationship_kwargs={"passive_deletes": True},
    )
    cart_items: list["CartItem"] = Relationship(
        back_populates="user",
        sa_relationship_kwargs={"passive_deletes": True},
    )
    orders: list["Order"] = Relationship(
        back_populates="user",
        sa_relationship_kwargs={"passive_deletes": True},
    )
    transactions: list["Transaction"] = Relationship(
        back_populates="user",
        sa_relationship_kwargs={"passive_deletes": True},
    )
