from datetime import datetime
from typing import TYPE_CHECKING, Optional
from sqlmodel import Field, SQLModel, Relationship

if TYPE_CHECKING:
    from model.user import User
    from model.product import Product


class Order(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    total_amount: float
    status: str = Field(default="pending")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    user_id: int = Field(foreign_key="user.id", ondelete="CASCADE", index=True)

    user: "User" = Relationship(back_populates="orders")
    order_items: list["OrderItem"] = Relationship(
        back_populates="order",
        sa_relationship_kwargs={"passive_deletes": True},
    )
    transaction: Optional["Transaction"] = Relationship(
        back_populates="order",
        sa_relationship_kwargs={"passive_deletes": True, "uselist": False},
    )


class OrderItem(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    quantity: int
    price_at_purchase: float
    order_id: int = Field(foreign_key="order.id", ondelete="CASCADE", index=True)
    product_id: int = Field(foreign_key="product.id", ondelete="CASCADE", index=True)

    order: "Order" = Relationship(back_populates="order_items")
    product: "Product" = Relationship(back_populates="order_items")


class Transaction(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    amount: float
    type: str
    category: str = Field(index=True)
    date: datetime = Field(default_factory=datetime.utcnow, index=True)
    notes: str | None = None
    user_id: int = Field(foreign_key="user.id", ondelete="CASCADE", index=True)
    order_id: int | None = Field(default=None, foreign_key="order.id", ondelete="CASCADE")

    user: "User" = Relationship(back_populates="transactions")
    order: Optional["Order"] = Relationship(back_populates="transaction")
