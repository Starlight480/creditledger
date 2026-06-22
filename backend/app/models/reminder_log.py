"""ReminderLog model — tracks all reminder notifications sent."""

from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from app.core.database import Base


class ReminderLog(Base):
    __tablename__ = "reminder_logs"

    id = Column(Integer, primary_key=True, index=True)
    credit_id = Column(Integer, ForeignKey("credits.id", ondelete="CASCADE"), nullable=False)
    channel = Column(String(20), default="whatsapp")
    status = Column(String(20), default="sent")
    message = Column(Text, nullable=True)
    external_id = Column(String(255), nullable=True)
    sent_at = Column(DateTime, default=datetime.utcnow)
    created_at = Column(DateTime, default=datetime.utcnow)

    credit = relationship("Credit", back_populates="reminder_logs")
