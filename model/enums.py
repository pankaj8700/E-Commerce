from enum import Enum


class Role(str, Enum):
    user = "user"
    admin = "admin"


class OrderStatus(str, Enum):
    pending = "pending"
    confirmed = "confirmed"
    cancelled = "cancelled"


class TransactionType(str, Enum):
    income = "income"
    expense = "expense"
