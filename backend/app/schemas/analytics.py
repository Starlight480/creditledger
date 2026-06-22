"""Analytics schemas."""

from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from decimal import Decimal


class DashboardSummary(BaseModel):
    total_credits: int
    total_amount_disbursed: Decimal
    total_outstanding: Decimal
    total_collected: Decimal
    overdue_count: int
    overdue_amount: Decimal
    active_debtors: int


class TrendPoint(BaseModel):
    period: str
    credits_count: int
    credits_amount: Decimal
    payments_amount: Decimal


class TrendsResponse(BaseModel):
    points: list[TrendPoint]


class OverdueItem(BaseModel):
    credit_id: int
    debtor_name: str
    debtor_phone: Optional[str]
    amount: Decimal
    balance_due: Decimal
    due_date: Optional[datetime]
    days_overdue: int


class OverdueResponse(BaseModel):
    items: list[OverdueItem]
    total: int
    total_amount: Decimal
