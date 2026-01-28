from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from datetime import date
from typing import Optional

from app.database import get_db
from app import models
from app.dependencies import get_current_user
from app.schemas import LedgerUpdateRequest



router = APIRouter(
    prefix="/api/ledger",
    tags=["ledger"],
)

# ======================================================
# 1️⃣ 결제 → 가계부 생성 (payment 승인 기반)
# ======================================================
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
        raise HTTPException(
            status_code=400,
            detail="승인된 결제만 가계부로 등록할 수 있습니다."
        )

    # 이미 ledger 있는지 확인
    existing = db.query(models.LedgerEntry).filter(
        models.LedgerEntry.payment_id == payment_id
    ).first()

    if existing:
        raise HTTPException(
            status_code=409,
            detail="이미 가계부에 등록된 결제입니다."
        )

    # ledger 생성
    ledger = models.LedgerEntry(
        user_id=payment.user_id,
        payment_id=payment.payment_id,
        spend_date=date.today(),
        category=models.LedgerCategory.GROCERY,  # TODO: 추후 결제 품목 기반 매핑
        amount=payment.total_amount,
        memo="카카오페이 결제",
    )

    db.add(ledger)
    db.commit()
    db.refresh(ledger)

    return ledger


# ======================================================
# 2️⃣ 가계부 목록 조회
# ======================================================
@router.get("")
def get_ledger_list(
    user_id: int = Query(..., description="사용자 ID"),
    start_date: Optional[date] = Query(None, description="조회 시작일"),
    end_date: Optional[date] = Query(None, description="조회 종료일"),
    category: Optional[models.LedgerCategory] = Query(None, description="카테고리"),
    db: Session = Depends(get_db),
):
    query = db.query(models.LedgerEntry).filter(
        models.LedgerEntry.user_id == user_id
    )

    # 날짜 필터
    if start_date:
        query = query.filter(models.LedgerEntry.spend_date >= start_date)

    if end_date:
        query = query.filter(models.LedgerEntry.spend_date <= end_date)

    # 카테고리 필터
    if category:
        query = query.filter(models.LedgerEntry.category == category)

    ledgers = (
        query
        .order_by(models.LedgerEntry.spend_date.desc())
        .all()
    )

    return [
        {
            "ledger_entry_id": l.ledger_entry_id,
            "payment_id": l.payment_id,
            "spend_date": l.spend_date,
            "category": l.category,
            "amount": l.amount,
            "memo": l.memo,
        }
        for l in ledgers
    ]

# ======================================================
# 3️⃣ 가계부 단건 조회 (JWT 인증 + 본인 데이터만)
# ======================================================
@router.get("/{ledger_entry_id}")
def get_ledger_detail(
    ledger_entry_id: int,
    db: Session = Depends(get_db),
    # 프로젝트에 이미 쓰고 있는 인증 의존성 사용
    current_user: models.AppUser = Depends(get_current_user),
):
    ledger = db.query(models.LedgerEntry).filter(
        models.LedgerEntry.ledger_entry_id == ledger_entry_id
    ).first()

    if not ledger:
        raise HTTPException(status_code=404, detail="가계부 항목을 찾을 수 없습니다.")

    # 본인 가계부만 조회 가능
    if ledger.user_id != current_user.user_id:
        raise HTTPException(status_code=403, detail="접근 권한이 없습니다.")

    return {
        "ledger_entry_id": ledger.ledger_entry_id,
        "payment_id": ledger.payment_id,
        "spend_date": ledger.spend_date,
        "category": ledger.category,
        "amount": ledger.amount,
        "memo": ledger.memo,
    }

# ======================================================
# 4️⃣ 가계부 수정 (카테고리 / 메모만)
# ======================================================
@router.put("/{ledger_entry_id}")
def update_ledger(
    ledger_entry_id: int,
    data: LedgerUpdateRequest,
    db: Session = Depends(get_db),
    current_user: models.AppUser = Depends(get_current_user),
):
    ledger = (
        db.query(models.LedgerEntry)
        .filter(models.LedgerEntry.ledger_entry_id == ledger_entry_id)
        .first()
    )

    if not ledger:
        raise HTTPException(status_code=404, detail="가계부 내역을 찾을 수 없습니다.")

    # 🔐 본인 데이터만 수정 가능
    if ledger.user_id != current_user.user_id:
        raise HTTPException(status_code=403, detail="접근 권한이 없습니다.")

    if data.category is not None:
        ledger.category = data.category

    if data.memo is not None:
        ledger.memo = data.memo

    db.commit()
    db.refresh(ledger)

    return {
        "ledger_entry_id": ledger.ledger_entry_id,
        "payment_id": ledger.payment_id,
        "spend_date": ledger.spend_date,
        "category": ledger.category,
        "amount": ledger.amount,
        "memo": ledger.memo,
    }
