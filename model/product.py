from typing import TYPE_CHECKING, Optional
from sqlalchemy import UniqueConstraint, Index
from sqlmodel import Field, SQLModel, Relationship

if TYPE_CHECKING:
    from model.user import User
    from model.cart import CartItem
    from model.order import OrderItem


class Category(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str = Field(unique=True, index=True)

    products: list["Product"] = Relationship(
        back_populates="category",
        sa_relationship_kwargs={"passive_deletes": True},
    )


class Product(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str = Field(unique=True, index=True)
    description: str = Field(max_length=255)
    price: float
    category_id: int | None = Field(default=None, foreign_key="category.id", index=True)

    category: Optional["Category"] = Relationship(back_populates="products")
    reviews: list["Review"] = Relationship(
        back_populates="product",
        sa_relationship_kwargs={"passive_deletes": True},
    )
    cart_items: list["CartItem"] = Relationship(
        back_populates="product",
        sa_relationship_kwargs={"passive_deletes": True},
    )
    order_items: list["OrderItem"] = Relationship(
        back_populates="product",
        sa_relationship_kwargs={"passive_deletes": True},
    )


class Review(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    text: str
    rating: int
    user_id: int = Field(foreign_key="user.id", index=True)
    product_id: int = Field(foreign_key="product.id")

    user: "User" = Relationship(back_populates="reviews")
    product: "Product" = Relationship(back_populates="reviews")

    __table_args__ = (
        Index("ix_review_product_id_id", "product_id", "id"),
        UniqueConstraint("user_id", "product_id", name="uq_review_user_product"),
    )
