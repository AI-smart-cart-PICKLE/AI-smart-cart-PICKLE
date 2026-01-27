import httpx
import os
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import HTMLResponse, JSONResponse
from sqlalchemy.orm import Session
from datetime import datetime
from .ledger import create_ledger_from_payment

from ..database import get_db
from .. import models, schemas

BASE_URL = os.getenv("BASE_URL", "http://localhost:8000")
KAKAO_ADMIN_KEY = os.getenv("KAKAO_ADMIN_KEY")

router = APIRouter(
    prefix="/api/payments",
    tags=["payments"],
    responses={404: {"description": "Not found"}},
)

# --- 1. 결제 준비 (Ready) ---
@router.post("/ready", response_model=schemas.PaymentReadyResponse)
async def payment_ready(
    request: schemas.PaymentReadyRequest,
    db: Session = Depends(get_db),
    user_id: int = 1
):
    cart_session = db.query(models.CartSession).filter(
        models.CartSession.cart_session_id == request.cart_session_id
    ).first()
    
    if not cart_session:
        raise HTTPException(status_code=404, detail="해당 카트 세션을 찾을 수 없습니다.")

    existing_payment = db.query(models.Payment).filter(
        models.Payment.cart_session_id == request.cart_session_id
    ).first()
    
    if existing_payment:
        db.delete(existing_payment)
        db.commit()

    url = "https://kapi.kakao.com/v1/payment/ready"
    headers = {
        "Authorization": f"KakaoAK {KAKAO_ADMIN_KEY}",
        "Content-type": "application/x-www-form-urlencoded;charset=utf-8"
    }
    
    data = {
        "cid": "TC0ONETIME", 
        "partner_order_id": str(cart_session.cart_session_id),
        "partner_user_id": str(user_id),
        "item_name": "스마트 장보기 결제",
        "quantity": 1,
        "total_amount": request.total_amount,
        "tax_free_amount": 0,
        "approval_url": f"{BASE_URL}/api/payments/success",
        "cancel_url": f"{BASE_URL}/api/payments/cancel",
        "fail_url": f"{BASE_URL}/api/payments/fail",
    }

    async with httpx.AsyncClient() as client:
        response = await client.post(url, headers=headers, data=data)
        res_data = response.json()

    if "tid" not in res_data:
        raise HTTPException(status_code=400, detail=f"KakaoPay Error: {res_data}")

    new_payment = models.Payment(
        cart_session_id=cart_session.cart_session_id,
        user_id=user_id,
        pg_provider=models.PgProviderType.KAKAO_PAY,
        pg_tid=res_data['tid'],
        status=models.PaymentStatus.PENDING,
        total_amount=request.total_amount,
        method_id=request.method_id
    )
    db.add(new_payment)
    db.commit()

    return schemas.PaymentReadyResponse(
        tid=res_data['tid'],
        next_redirect_app_url=res_data.get('next_redirect_app_url'),
        next_redirect_mobile_url=res_data.get('next_redirect_mobile_url'),
        next_redirect_pc_url=res_data.get('next_redirect_pc_url')
    )


# --- 2. 결제 승인 (Approve) ---
@router.post("/approve", response_model=schemas.PaymentResponse)
async def payment_approve(
    request: schemas.PaymentApproveRequest,
    db: Session = Depends(get_db),
    user_id: int = 1
):
    payment = db.query(models.Payment).filter(
        models.Payment.pg_tid == request.tid,
        models.Payment.user_id == user_id,
        models.Payment.status == models.PaymentStatus.PENDING
    ).first()

    if not payment:
        raise HTTPException(status_code=404, detail="대기 중인 결제 정보를 찾을 수 없습니다.")

    url = "https://kapi.kakao.com/v1/payment/approve"
    headers = {
        "Authorization": f"KakaoAK {KAKAO_ADMIN_KEY}",
        "Content-type": "application/x-www-form-urlencoded;charset=utf-8"
    }
    data = {
        "cid": "TC0ONETIME",
        "tid": request.tid,
        "partner_order_id": str(payment.cart_session_id),
        "partner_user_id": str(user_id),
        "pg_token": request.pg_token
    }

    async with httpx.AsyncClient() as client:
        response = await client.post(url, headers=headers, data=data)
        res_data = response.json()

    if "aid" not in res_data:
        payment.status = models.PaymentStatus.FAILED
        db.commit()
        raise HTTPException(status_code=400, detail=f"Approval failed: {res_data}")

    payment.status = models.PaymentStatus.APPROVED
    payment.approved_at = datetime.now()
    
    cart_session = db.query(models.CartSession).filter(
        models.CartSession.cart_session_id == payment.cart_session_id
    ).first()
    
    if cart_session:
        cart_session.status = models.CartSessionStatus.PAID
        cart_session.ended_at = datetime.now()

    db.commit()
    db.refresh(payment)

    try:
        create_ledger_from_payment(payment_id=payment.payment_id, db=db)
        print(f"✅ 가계부 자동 등록 완료: Payment ID {payment.payment_id}")
    except Exception as e:
        print(f"⚠️ 가계부 등록 실패 (결제는 성공): {e}")

    return payment


# --- 3. 콜백 URL ---
@router.get("/success", response_class=HTMLResponse)
async def payment_success_callback(pg_token: str):
    return HTMLResponse(content=f"""
    <html>
        <head><title>결제 성공</title></head>
        <body style="display:flex; flex-direction:column; align-items:center; justify-content:center; height:100vh;">
            <h1 style="color:green;">✅ 인증 성공!</h1>
            <p>토큰: <b>{pg_token}</b></p>
        </body>
    </html>
    """)

@router.get("/cancel")
async def payment_cancel_callback():
    return JSONResponse(content={"message": "결제 취소", "status": "CANCELLED"})

@router.get("/fail")
async def payment_fail_callback():
    return JSONResponse(content={"message": "결제 실패", "status": "FAILED"}, status_code=400)


# ========================================================
# 🚨 [순서 중요] /methods가 /{payment_id}보다 무조건 위에 있어야 함!
# ========================================================

# --- 6. 결제 수단(카드) 목록 조회 ---
@router.get("/methods", response_model=list[schemas.PaymentMethodResponse])
async def get_payment_methods(
    db: Session = Depends(get_db),
    user_id: int = 1
):
    methods = db.query(models.PaymentMethod).filter(
        models.PaymentMethod.user_id == user_id
    ).all()
    return methods


# --- 7. 결제 수단 등록 ---
@router.post("/methods", response_model=schemas.PaymentMethodResponse)
async def register_payment_method(
    request: schemas.PaymentMethodCreate,
    db: Session = Depends(get_db),
    user_id: int = 1
):
    existing_count = db.query(models.PaymentMethod).filter(
        models.PaymentMethod.user_id == user_id
    ).count()
    
    is_default = (existing_count == 0)

    new_method = models.PaymentMethod(
        user_id=user_id,
        method_type=request.method_type,
        card_brand=request.card_brand,
        card_last4=request.card_last4,
        billing_key=request.billing_key,
        is_default=is_default or request.is_default
    )
    
    db.add(new_method)
    db.commit()
    db.refresh(new_method)
    
    return new_method


# --- 8. 결제 수단 삭제 ---
@router.delete("/methods/{method_id}")
async def delete_payment_method(
    method_id: int,
    db: Session = Depends(get_db),
    user_id: int = 1
):
    method = db.query(models.PaymentMethod).filter(
        models.PaymentMethod.method_id == method_id,
        models.PaymentMethod.user_id == user_id
    ).first()

    if not method:
        raise HTTPException(status_code=404, detail="결제 수단을 찾을 수 없습니다.")

    db.delete(method)
    db.commit()

    return {"message": "결제 수단이 삭제되었습니다."}


# --- 4. 결제 상세 조회 ---
@router.get("/{payment_id}", response_model=schemas.PaymentDetailResponse)
async def get_payment_detail(
    payment_id: int,
    db: Session = Depends(get_db),
    user_id: int = 1
):
    payment = db.query(models.Payment).filter(
        models.Payment.payment_id == payment_id,
        models.Payment.user_id == user_id
    ).first()

    if not payment:
        raise HTTPException(status_code=404, detail="결제 내역을 찾을 수 없습니다.")

    return payment


# --- 5. 결제 취소(환불) ---
@router.post("/{payment_id}/cancel", response_model=schemas.PaymentResponse)
async def cancel_payment(
    payment_id: int,
    request: schemas.PaymentCancelRequest,
    db: Session = Depends(get_db),
    user_id: int = 1
):
    payment = db.query(models.Payment).filter(
        models.Payment.payment_id == payment_id,
        models.Payment.user_id == user_id
    ).first()

    if not payment:
        raise HTTPException(status_code=404, detail="결제 내역을 찾을 수 없습니다.")

    if payment.status != models.PaymentStatus.APPROVED:
        raise HTTPException(status_code=400, detail="승인 완료된 결제만 취소할 수 있습니다.")

    url = "https://kapi.kakao.com/v1/payment/cancel"
    headers = {
        "Authorization": f"KakaoAK {KAKAO_ADMIN_KEY}",
        "Content-type": "application/x-www-form-urlencoded;charset=utf-8"
    }
    data = {
        "cid": "TC0ONETIME",
        "tid": payment.pg_tid,
        "cancel_amount": payment.total_amount,
        "cancel_tax_free_amount": 0,
    }

    async with httpx.AsyncClient() as client:
        response = await client.post(url, headers=headers, data=data)
        res_data = response.json()

    if "tid" not in res_data:
        raise HTTPException(status_code=400, detail=f"Cancel failed: {res_data}")

    payment.status = models.PaymentStatus.CANCELLED 
    
    db.commit()
    db.refresh(payment)

    return payment