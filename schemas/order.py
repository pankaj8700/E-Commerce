from datetime import datetime
from pydantic import BaseModel
from model.enums import OrderStatus


class OrderStatusUpdate(BaseModel):
    status: OrderStatus  # confirmed / cancelled


class OrderItemResponse(BaseModel):
    id: int
    product_id: int
    quantity: int
    price_at_purchase: float

    model_config = {"from_attributes": True}


class OrderResponse(BaseModel):
    id: int
    total_amount: float
    status: str
    created_at: datetime

    model_config = {"from_attributes": True}


class OrderDetailResponse(BaseModel):
    order: OrderResponse
    items: list[OrderItemResponse]
