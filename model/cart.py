from typing import TYPE_CHECKING
from sqlalchemy import UniqueConstraint
from sqlmodel import Field, SQLModel, Relationship

if TYPE_CHECKING:
    from model.user import User
    from model.product import Product


class CartItem(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    quantity: int = Field(default=1, ge=1)
    user_id: int = Field(foreign_key="user.id", index=True)
    product_id: int = Field(foreign_key="product.id", index=True)

    user: "User" = Relationship(back_populates="cart_items")
    product: "Product" = Relationship(back_populates="cart_items")

    __table_args__ = (
        UniqueConstraint("user_id", "product_id", name="uq_cart_user_product"),
    )
