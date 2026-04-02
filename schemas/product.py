from typing import Optional
from pydantic import BaseModel, Field


class ProductCreate(BaseModel):
    name: str
    description: str
    price: float
    category_id: Optional[int] = Field(default=None, gt=0)


class ProductUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    price: Optional[float] = None
    category_id: Optional[int] = Field(default=None, gt=0)


class CategoryCreate(BaseModel):
    name: str
