from datetime import datetime
from pydantic import BaseModel


class TransactionResponse(BaseModel):
    id: int
    amount: float
    type: str
    category: str
    date: datetime
    notes: str | None
    user_id: int
    order_id: int | None

    model_config = {"from_attributes": True}


class UserDashboardSummary(BaseModel):
    total_expense: float
    total_orders: int


class AdminDashboardSummary(BaseModel):
    total_revenue: float
    pending_amount: float
    cancelled_amount: float
    total_orders: int
