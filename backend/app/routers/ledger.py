from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from datetime import date
from typing import Optional

from app.database import get_db
from app import models
from app.dependencies import get_current_user
from app.schemas import LedgerUpdateRequest

from sqlalchemy import func
from calendar import monthrange





router = APIRouter(
    prefix="/ledger",
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
# 6️⃣ 월별 가계부 캘린더 조회 (날짜별 지출 합계)
# ======================================================
@router.get("/calendar")
def get_ledger_calendar(
    year: int = Query(..., ge=2000, description="조회 연도"),
    month: int = Query(..., ge=1, le=12, description="조회 월 (1~12)"),
    db: Session = Depends(get_db),
    current_user: models.AppUser = Depends(get_current_user),
):
    # 월 시작 / 종료일 계산
    start_date = date(year, month, 1)
    last_day = monthrange(year, month)[1]
    end_date = date(year, month, last_day)

    rows = (
        db.query(
            models.LedgerEntry.spend_date,
            func.sum(models.LedgerEntry.amount).label("total_amount"),
        )
        .filter(
            models.LedgerEntry.user_id == current_user.user_id,
            models.LedgerEntry.spend_date >= start_date,
            models.LedgerEntry.spend_date <= end_date,
        )
        .group_by(models.LedgerEntry.spend_date)
        .order_by(models.LedgerEntry.spend_date)
        .all()
    )

    daily_total = {}
    for spend_date, total_amount in rows:
        daily_total[str(spend_date)] = int(total_amount)

    return {
        "year": year,
        "month": month,
        "daily_total": daily_total,
    }

# ======================================================
# 5️⃣ 월별 가계부 요약 조회
# ======================================================
@router.get("/summary/monthly")
def get_monthly_summary(
    year: int = Query(..., ge=2000, description="조회 연도"),
    month: int = Query(..., ge=1, le=12, description="조회 월 (1~12)"),
    db: Session = Depends(get_db),
    current_user: models.AppUser = Depends(get_current_user),
):
    # 월 시작 / 종료일 계산
    start_date = date(year, month, 1)
    last_day = monthrange(year, month)[1]
    end_date = date(year, month, last_day)

    # 카테고리별 합계 조회
    rows = (
        db.query(
            models.LedgerEntry.category,
            func.sum(models.LedgerEntry.amount).label("amount"),
        )
        .filter(
            models.LedgerEntry.user_id == current_user.user_id,
            models.LedgerEntry.spend_date >= start_date,
            models.LedgerEntry.spend_date <= end_date,
        )
        .group_by(models.LedgerEntry.category)
        .all()
    )

    by_category = [
        {
            "category": category,
            "amount": amount,
        }
        for category, amount in rows
    ]

    total_amount = sum(item["amount"] for item in by_category)

    # 🔹 ratio(%) 계산
    for item in by_category:
        item["ratio"] = round(item["amount"] / total_amount * 100) if total_amount > 0 else 0

    by_category.sort(key=lambda x: x["amount"], reverse=True)
    return {
        "year": year,
        "month": month,
        "total_amount": total_amount,
        "by_category": by_category,
    }

# ======================================================
# 7️⃣ Top Categories 조회 (지출 금액 기준)
# ======================================================
@router.get("/top-categories")
def get_top_categories(
    year: int = Query(..., ge=2000, description="조회 연도"),
    month: int = Query(..., ge=1, le=12, description="조회 월 (1~12)"),
    limit: int = Query(5, ge=1, le=10, description="상위 카테고리 개수"),
    db: Session = Depends(get_db),
    current_user: models.AppUser = Depends(get_current_user),
):
    # 월 시작 / 종료일 계산
    start_date = date(year, month, 1)
    last_day = monthrange(year, month)[1]
    end_date = date(year, month, last_day)

    rows = (
        db.query(
            models.LedgerEntry.category,
            func.sum(models.LedgerEntry.amount).label("amount"),
        )
        .filter(
            models.LedgerEntry.user_id == current_user.user_id,
            models.LedgerEntry.spend_date >= start_date,
            models.LedgerEntry.spend_date <= end_date,
        )
        .group_by(models.LedgerEntry.category)
        .order_by(func.sum(models.LedgerEntry.amount).desc())
        .limit(limit)
        .all()
    )

    categories = [
        {
            "category": category,
            "amount": amount,
        }
        for category, amount in rows
    ]

    total_amount = sum(item["amount"] for item in categories)

    for item in categories:
        item["ratio"] = round(item["amount"] / total_amount * 100) if total_amount > 0 else 0

    return {
        "year": year,
        "month": month,
        "categories": categories,
    }

# ======================================================
# 8️⃣ Top Items 조회 (구매 횟수 기준 - 임시: 카테고리 사용)
# ======================================================
@router.get("/top-items")
def get_top_items(
    year: int = Query(..., ge=2000, description="조회 연도"),
    month: int = Query(..., ge=1, le=12, description="조회 월 (1~12)"),
    limit: int = Query(5, ge=1, le=10, description="상위 아이템 개수"),
    db: Session = Depends(get_db),
    current_user: models.AppUser = Depends(get_current_user),
):
    start_date = date(year, month, 1)
    last_day = monthrange(year, month)[1]
    end_date = date(year, month, last_day)

    rows = (
        db.query(
            models.LedgerEntry.category.label("item_name"),
            func.count(models.LedgerEntry.ledger_entry_id).label("count"),
            func.sum(models.LedgerEntry.amount).label("total_amount"),
        )
        .filter(
            models.LedgerEntry.user_id == current_user.user_id,
            models.LedgerEntry.spend_date >= start_date,
            models.LedgerEntry.spend_date <= end_date,
        )
        .group_by(models.LedgerEntry.category)
        .order_by(
            func.count(models.LedgerEntry.ledger_entry_id).desc(),
            func.sum(models.LedgerEntry.amount).desc(),
        )
        .limit(limit)
        .all()
    )

    items = [
        {
            "item_name": item_name,
            "count": count,
            "total_amount": total_amount,
        }
        for item_name, count, total_amount in rows
    ]

    return {
        "year": year,
        "month": month,
        "items": items,
    }

# ======================================================
# 9️⃣ 최근 지출 내역 조회
# ======================================================
@router.get("/recent")
def get_recent_ledger(
    limit: int = Query(5, ge=1, le=20),
    db: Session = Depends(get_db),
    current_user: models.AppUser = Depends(get_current_user),
):
    rows = (
        db.query(models.LedgerEntry, models.Payment)
        .join(
            models.Payment,
            models.LedgerEntry.payment_id == models.Payment.payment_id,
        )
        .filter(
            models.LedgerEntry.user_id == current_user.user_id,
            models.Payment.status == models.PaymentStatus.APPROVED,
        )
        .order_by(models.LedgerEntry.ledger_entry_id.desc())
        .limit(limit)
        .all()
    )

    items = []
    for ledger, payment in rows:
        items.append({
            "ledger_entry_id": ledger.ledger_entry_id,
            "payment_id": payment.payment_id,
            "spend_date": ledger.spend_date,
            "amount": ledger.amount,
            "category": ledger.category,
            "memo": ledger.memo,
        })

    return {"items": items}


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



