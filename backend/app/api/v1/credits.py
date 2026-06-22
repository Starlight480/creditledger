"""Credit routes — create, list, update, record payment."""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import or_, func

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.models.credit import Credit
from app.models.debtor import Debtor
from app.models.payment import Payment
from app.schemas.credit import (
    CreditCreate, CreditUpdate, CreditResponse, CreditListResponse,
)
from app.schemas.payment import PaymentCreate, PaymentResponse, PaymentListResponse

router = APIRouter()


@router.get("", response_model=CreditListResponse)
def list_credits(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    status: str = Query(None),
    search: str = Query(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    query = db.query(Credit).filter(
        Credit.business_id == current_user.business_id,
        Credit.is_active == True,
    )

    if status:
        query = query.filter(Credit.status == status)
    if search:
        query = query.join(Debtor).filter(
            or_(
                Debtor.name.ilike(f"%{search}%"),
                Credit.description.ilike(f"%{search}%"),
            )
        )

    total = query.count()
    items = query.order_by(Credit.created_at.desc()).offset((page - 1) * page_size).limit(page_size).all()

    return CreditListResponse(
        items=[CreditResponse.model_validate(c) for c in items],
        total=total,
        page=page,
        page_size=page_size,
    )


@router.post("", response_model=CreditResponse, status_code=201)
def create_credit(
    req: CreditCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    # Verify debtor belongs to this business
    debtor = db.query(Debtor).filter(
        Debtor.id == req.debtor_id,
        Debtor.business_id == current_user.business_id,
        Debtor.is_active == True,
    ).first()
    if not debtor:
        raise HTTPException(status_code=404, detail="Debtor not found")

    credit = Credit(
        business_id=current_user.business_id,
        debtor_id=req.debtor_id,
        amount=req.amount,
        balance_due=req.amount,
        description=req.description,
        due_date=req.due_date,
    )
    db.add(credit)
    db.commit()
    db.refresh(credit)
    return credit


@router.get("/{credit_id}", response_model=CreditResponse)
def get_credit(
    credit_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    credit = db.query(Credit).filter(
        Credit.id == credit_id,
        Credit.business_id == current_user.business_id,
    ).first()
    if not credit:
        raise HTTPException(status_code=404, detail="Credit not found")
    return credit


@router.put("/{credit_id}", response_model=CreditResponse)
def update_credit(
    credit_id: int,
    req: CreditUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    credit = db.query(Credit).filter(
        Credit.id == credit_id,
        Credit.business_id == current_user.business_id,
    ).first()
    if not credit:
        raise HTTPException(status_code=404, detail="Credit not found")

    for field, value in req.model_dump(exclude_unset=True).items():
        setattr(credit, field, value)

    db.commit()
    db.refresh(credit)
    return credit


@router.post("/{credit_id}/payments", response_model=PaymentResponse, status_code=201)
def record_payment(
    credit_id: int,
    req: PaymentCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    credit = db.query(Credit).filter(
        Credit.id == credit_id,
        Credit.business_id == current_user.business_id,
    ).first()
    if not credit:
        raise HTTPException(status_code=404, detail="Credit not found")

    if credit.status == "paid":
        raise HTTPException(status_code=400, detail="Credit is already fully paid")

    if req.amount > credit.balance_due:
        raise HTTPException(
            status_code=400,
            detail=f"Payment amount ({req.amount}) exceeds balance due ({credit.balance_due})",
        )

    from datetime import datetime
    payment = Payment(
        credit_id=credit_id,
        amount=req.amount,
        method=req.method,
        reference=req.reference,
        notes=req.notes,
        paid_at=req.paid_at or datetime.utcnow(),
    )
    db.add(payment)

    # Update credit balance
    credit.balance_due -= req.amount
    if credit.balance_due <= 0:
        credit.balance_due = 0
        credit.status = "paid"

    db.commit()
    db.refresh(payment)
    return payment


@router.get("/{credit_id}/payments", response_model=PaymentListResponse)
def get_payments(
    credit_id: int,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    credit = db.query(Credit).filter(
        Credit.id == credit_id,
        Credit.business_id == current_user.business_id,
    ).first()
    if not credit:
        raise HTTPException(status_code=404, detail="Credit not found")

    query = db.query(Payment).filter(Payment.credit_id == credit_id)
    total = query.count()
    items = query.order_by(Payment.paid_at.desc()).offset((page - 1) * page_size).limit(page_size).all()

    return PaymentListResponse(
        items=[PaymentResponse.model_validate(p) for p in items],
        total=total,
        page=page,
        page_size=page_size,
    )
