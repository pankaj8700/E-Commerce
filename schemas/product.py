from pydantic import BaseModel, Field


class ProductCreate(BaseModel):
    name: str
    description: str
    price: float
    category_id: int | None = Field(default=None, gt=0)


class ProductUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
    price: float | None = None
    category_id: int | None = Field(default=None, gt=0)


class CategoryCreate(BaseModel):
    name: str


class CategoryResponse(BaseModel):
    id: int
    name: str

    model_config = {"from_attributes": True}


class ProductResponse(BaseModel):
    id: int
    name: str
    description: str
    price: float
    category_id: int | None

    model_config = {"from_attributes": True}
