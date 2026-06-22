"""Debtor schemas."""

from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class DebtorCreate(BaseModel):
    name: str = Field(..., min_length=2, max_length=255)
    phone: Optional[str] = None
    email: Optional[str] = None
    address: Optional[str] = None
    notes: Optional[str] = None


class DebtorUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=2, max_length=255)
    phone: Optional[str] = None
    email: Optional[str] = None
    address: Optional[str] = None
    notes: Optional[str] = None


class DebtorResponse(BaseModel):
    id: int
    business_id: int
    name: str
    phone: Optional[str]
    email: Optional[str]
    address: Optional[str]
    notes: Optional[str]
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class DebtorListResponse(BaseModel):
    items: list[DebtorResponse]
    total: int
    page: int
    page_size: int
