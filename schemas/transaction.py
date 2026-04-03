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


class DashboardSummary(BaseModel):
    total_income: float
    total_expense: float
    net_balance: float
    total_transactions: int
