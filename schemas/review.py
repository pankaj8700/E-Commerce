from pydantic import BaseModel, Field


class ReviewCreate(BaseModel):
    text: str
    rating: int = Field(ge=1, le=5)
    product_id: int


class ReviewResponse(BaseModel):
    id: int
    text: str
    rating: int
    user_id: int
    product_id: int

    model_config = {"from_attributes": True}
