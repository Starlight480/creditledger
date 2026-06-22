"""Analytics routes — dashboard summary, trends, overdue report."""

from datetime import datetime, timedelta
from decimal import Decimal
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func, and_

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.models.credit import Credit
from app.models.debtor import Debtor
from app.models.payment import Payment
from app.schemas.analytics import (
    DashboardSummary, TrendsResponse, TrendPoint,
    OverdueResponse, OverdueItem,
)

router = APIRouter()


@router.get("/summary", response_model=DashboardSummary)
def get_summary(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    business_id = current_user.business_id

    # Total credits
    credits_q = db.query(Credit).filter(
        Credit.business_id == business_id,
        Credit.is_active == True,
    )
    total_credits = credits_q.count()
    total_amount = db.query(func.coalesce(func.sum(Credit.amount), 0)).filter(
        Credit.business_id == business_id,
        Credit.is_active == True,
    ).scalar()

    # Outstanding
    total_outstanding = db.query(func.coalesce(func.sum(Credit.balance_due), 0)).filter(
        Credit.business_id == business_id,
        Credit.is_active == True,
    ).scalar()

    # Collected
    total_collected = db.query(func.coalesce(func.sum(Payment.amount), 0)).filter(
        Payment.credit_id.in_(
            db.query(Credit.id).filter(Credit.business_id == business_id)
        )
    ).scalar()

    # Overdue
    now = datetime.utcnow()
    overdue_q = db.query(Credit).filter(
        Credit.business_id == business_id,
        Credit.is_active == True,
        Credit.status == "active",
        Credit.due_date < now,
    )
    overdue_count = overdue_q.count()
    overdue_amount = db.query(func.coalesce(func.sum(Credit.balance_due), 0)).filter(
        Credit.business_id == business_id,
        Credit.is_active == True,
        Credit.status == "active",
        Credit.due_date < now,
    ).scalar()

    # Active debtors
    active_debtors = db.query(func.count(func.distinct(Credit.debtor_id))).filter(
        Credit.business_id == business_id,
        Credit.is_active == True,
        Credit.status == "active",
    ).scalar()

    return DashboardSummary(
        total_credits=total_credits,
        total_amount_disbursed=total_amount,
        total_outstanding=total_outstanding,
        total_collected=total_collected,
        overdue_count=overdue_count,
        overdue_amount=overdue_amount,
        active_debtors=active_debtors,
    )


@router.get("/trends", response_model=TrendsResponse)
def get_trends(
    months: int = 6,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    business_id = current_user.business_id
    now = datetime.utcnow()
    points = []

    for i in range(months - 1, -1, -1):
        month_start = (now.replace(day=1) - timedelta(days=i * 30)).replace(day=1)
        month_end = (month_start + timedelta(days=32)).replace(day=1)

        credits_count = db.query(func.count(Credit.id)).filter(
            Credit.business_id == business_id,
            Credit.issued_at >= month_start,
            Credit.issued_at < month_end,
        ).scalar()

        credits_amount = db.query(func.coalesce(func.sum(Credit.amount), 0)).filter(
            Credit.business_id == business_id,
            Credit.issued_at >= month_start,
            Credit.issued_at < month_end,
        ).scalar()

        payments_amount = db.query(func.coalesce(func.sum(Payment.amount), 0)).filter(
            Payment.credit_id.in_(
                db.query(Credit.id).filter(Credit.business_id == business_id)
            ),
            Payment.paid_at >= month_start,
            Payment.paid_at < month_end,
        ).scalar()

        points.append(TrendPoint(
            period=month_start.strftime("%Y-%m"),
            credits_count=credits_count,
            credits_amount=credits_amount,
            payments_amount=payments_amount,
        ))

    return TrendsResponse(points=points)


@router.get("/overdue", response_model=OverdueResponse)
def get_overdue(
    page: int = 1,
    page_size: int = 20,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    business_id = current_user.business_id
    now = datetime.utcnow()

    query = db.query(Credit, Debtor).join(Debtor, Credit.debtor_id == Debtor.id).filter(
        Credit.business_id == business_id,
        Credit.is_active == True,
        Credit.status == "active",
        Credit.due_date < now,
    ).order_by(Credit.due_date.asc())

    total = query.count()
    rows = query.offset((page - 1) * page_size).limit(page_size).all()

    items = []
    total_amount = Decimal("0")
    for credit, debtor in rows:
        days_overdue = (now - credit.due_date).days
        items.append(OverdueItem(
            credit_id=credit.id,
            debtor_name=debtor.name,
            debtor_phone=debtor.phone,
            amount=credit.amount,
            balance_due=credit.balance_due,
            due_date=credit.due_date,
            days_overdue=days_overdue,
        ))
        total_amount += credit.balance_due

    return OverdueResponse(items=items, total=total, total_amount=total_amount)
