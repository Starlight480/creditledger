"""Credit schemas."""

from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from decimal import Decimal


class CreditCreate(BaseModel):
    debtor_id: int
    amount: Decimal = Field(..., gt=0, decimal_places=2)
    description: Optional[str] = None
    due_date: Optional[datetime] = None


class CreditUpdate(BaseModel):
    description: Optional[str] = None
    due_date: Optional[datetime] = None
    status: Optional[str] = None


class CreditResponse(BaseModel):
    id: int
    business_id: int
    debtor_id: int
    amount: Decimal
    balance_due: Decimal
    description: Optional[str]
    status: str
    issued_at: datetime
    due_date: Optional[datetime]
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class CreditListResponse(BaseModel):
    items: list[CreditResponse]
    total: int
    page: int
    page_size: int
