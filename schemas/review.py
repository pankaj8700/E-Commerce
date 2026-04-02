from pydantic import BaseModel, Field


class ReviewCreate(BaseModel):
    text: str
    rating: int = Field(ge=1, le=5)
    product_id: int
