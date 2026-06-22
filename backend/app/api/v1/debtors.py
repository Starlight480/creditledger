"""Debtor routes — CRUD + search + pagination."""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import or_

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.models.debtor import Debtor
from app.models.credit import Credit
from app.schemas.debtor import (
    DebtorCreate, DebtorUpdate, DebtorResponse, DebtorListResponse,
)

router = APIRouter()


@router.get("", response_model=DebtorListResponse)
def list_debtors(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    search: str = Query(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    query = db.query(Debtor).filter(
        Debtor.business_id == current_user.business_id,
        Debtor.is_active == True,
    )

    if search:
        query = query.filter(
            or_(
                Debtor.name.ilike(f"%{search}%"),
                Debtor.phone.ilike(f"%{search}%"),
                Debtor.email.ilike(f"%{search}%"),
            )
        )

    total = query.count()
    items = query.order_by(Debtor.created_at.desc()).offset((page - 1) * page_size).limit(page_size).all()

    return DebtorListResponse(
        items=[DebtorResponse.model_validate(d) for d in items],
        total=total,
        page=page,
        page_size=page_size,
    )


@router.post("", response_model=DebtorResponse, status_code=201)
def create_debtor(
    req: DebtorCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    debtor = Debtor(**req.model_dump(), business_id=current_user.business_id)
    db.add(debtor)
    db.commit()
    db.refresh(debtor)
    return debtor


@router.get("/{debtor_id}", response_model=DebtorResponse)
def get_debtor(
    debtor_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    debtor = db.query(Debtor).filter(
        Debtor.id == debtor_id,
        Debtor.business_id == current_user.business_id,
    ).first()
    if not debtor:
        raise HTTPException(status_code=404, detail="Debtor not found")
    return debtor


@router.put("/{debtor_id}", response_model=DebtorResponse)
def update_debtor(
    debtor_id: int,
    req: DebtorUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    debtor = db.query(Debtor).filter(
        Debtor.id == debtor_id,
        Debtor.business_id == current_user.business_id,
    ).first()
    if not debtor:
        raise HTTPException(status_code=404, detail="Debtor not found")

    for field, value in req.model_dump(exclude_unset=True).items():
        setattr(debtor, field, value)

    db.commit()
    db.refresh(debtor)
    return debtor


@router.delete("/{debtor_id}", status_code=204)
def delete_debtor(
    debtor_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    debtor = db.query(Debtor).filter(
        Debtor.id == debtor_id,
        Debtor.business_id == current_user.business_id,
    ).first()
    if not debtor:
        raise HTTPException(status_code=404, detail="Debtor not found")

    # Check for active credits
    active_credits = db.query(Credit).filter(
        Credit.debtor_id == debtor_id,
        Credit.status == "active",
    ).count()

    if active_credits > 0:
        raise HTTPException(
            status_code=400,
            detail=f"Cannot delete debtor with {active_credits} active credit(s). Settle or reassign first.",
        )

    debtor.is_active = False
    db.commit()
