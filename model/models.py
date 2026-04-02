from enum import Enum
from typing import List, Optional
from sqlalchemy import UniqueConstraint, Index
from sqlmodel import Field, SQLModel, Relationship


class Role(str, Enum):
    user = "user"
    admin = "admin"


class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    username: str = Field(max_length=20, unique=True, index=True)
    email: str = Field(unique=True, index=True)
    password: str = Field(max_length=128)
    role: str = Field(default=Role.user.value)

    reviews: List["Review"] = Relationship(
        back_populates="user",
        sa_relationship_kwargs={"passive_deletes": True},
    )


class Category(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(unique=True, index=True)

    products: List["Product"] = Relationship(
        back_populates="category",
        sa_relationship_kwargs={"passive_deletes": True},
    )


class Product(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(unique=True, index=True)
    description: str = Field(max_length=255)
    price: float
    category_id: Optional[int] = Field(
        default=None, foreign_key="category.id", index=True
    )

    category: Optional["Category"] = Relationship(back_populates="products")
    reviews: List["Review"] = Relationship(
        back_populates="product",
        sa_relationship_kwargs={"passive_deletes": True},
    )


class Review(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    text: str
    rating: int
    user_id: int = Field(foreign_key="user.id", index=True)
    product_id: int = Field(foreign_key="product.id")

    user: "User" = Relationship(back_populates="reviews")
    product: "Product" = Relationship(back_populates="reviews")

    __table_args__ = (
        # composite index: covers WHERE product_id = ? AND id > ? ORDER BY id
        Index("ix_review_product_id_id", "product_id", "id"),
        # one review per user per product
        UniqueConstraint("user_id", "product_id", name="uq_review_user_product"),
    )
