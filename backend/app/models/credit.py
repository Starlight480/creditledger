"""Credit model — a loan/credit sale given to a debtor."""

from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey, Numeric, Text
from sqlalchemy.orm import relationship
from app.core.database import Base


class Credit(Base):
    __tablename__ = "credits"

    id = Column(Integer, primary_key=True, index=True)
    business_id = Column(Integer, ForeignKey("businesses.id", ondelete="CASCADE"), nullable=False)
    debtor_id = Column(Integer, ForeignKey("debtors.id", ondelete="CASCADE"), nullable=False)
    amount = Column(Numeric(12, 2), nullable=False)
    balance_due = Column(Numeric(12, 2), nullable=False)
    description = Column(Text, nullable=True)
    status = Column(String(20), default="active")
    issued_at = Column(DateTime, default=datetime.utcnow)
    due_date = Column(DateTime, nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    business = relationship("Business", back_populates="credits")
    debtor = relationship("Debtor", back_populates="credits")
    payments = relationship("Payment", back_populates="credit", cascade="all, delete-orphan")
    reminder_logs = relationship("ReminderLog", back_populates="credit", cascade="all, delete-orphan")
