from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import date

from app.database import get_db
from app import models

router = APIRouter(
    prefix="/api/ledger",
    tags=["ledger"],
)

@router.post("/from-payment/{payment_id}")
def create_ledger_from_payment(
    payment_id: int,
    db: Session = Depends(get_db),
):
    # payment 조회
    payment = db.query(models.Payment).filter(
        models.Payment.payment_id == payment_id
    ).first()

    if not payment:
        raise HTTPException(status_code=404, detail="결제를 찾을 수 없습니다.")

    if payment.status != models.PaymentStatus.APPROVED:
        raise HTTPException(status_code=400, detail="승인된 결제만 가계부로 등록할 수 있습니다.")

    # 이미 ledger 있는지 확인
    existing = db.query(models.LedgerEntry).filter(
        models.LedgerEntry.payment_id == payment_id
    ).first()

    if existing:
        raise HTTPException(status_code=409, detail="이미 가계부에 등록된 결제입니다.")

    # ledger 생성
    ledger = models.LedgerEntry(
        user_id=payment.user_id,
        payment_id=payment.payment_id,
        spend_date=date.today(),
        category=models.LedgerCategory.GROCERY,  # 일단 고정
        amount=payment.total_amount,
        memo="카카오페이 결제",
    )

    db.add(ledger)
    db.commit()
    db.refresh(ledger)

    return ledger
