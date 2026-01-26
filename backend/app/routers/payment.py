import httpx
import os
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session
from datetime import datetime

# 데이터베이스 및 스키마 임포트
from ..database import get_db
from .. import models, schemas

router = APIRouter(
    prefix="/api/payments",
    tags=["payments"],
    responses={404: {"description": "Not found"}},
)

KAKAO_ADMIN_KEY = os.getenv("KAKAO_ADMIN_KEY")

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

    # [중복 방지] 기존에 시도하던 결제 건이 있으면 삭제하고 새로 시작
    existing_payment = db.query(models.Payment).filter(
        models.Payment.cart_session_id == request.cart_session_id
    ).first()
    
    if existing_payment:
        db.delete(existing_payment)
        db.commit()

    # 카카오페이 API 요청
    url = "https://kapi.kakao.com/v1/payment/ready"
    headers = {
        "Authorization": f"KakaoAK {KAKAO_ADMIN_KEY}",
        "Content-type": "application/x-www-form-urlencoded;charset=utf-8"
    }
    
    # [핵심] approval_url이 아래의 @router.get("/success") 주소와 정확히 일치해야 합니다.
    data = {
        "cid": "TC0ONETIME", 
        "partner_order_id": str(cart_session.cart_session_id),
        "partner_user_id": str(user_id),
        "item_name": "스마트 장보기 결제",
        "quantity": 1,
        "total_amount": request.total_amount,
        "tax_free_amount": 0,
        "approval_url": "http://localhost:8000/api/payments/success", # 여기가 도착지!
        "cancel_url": "http://localhost:8000/api/payments/cancel",
        "fail_url": "http://localhost:8000/api/payments/fail",
    }

    async with httpx.AsyncClient() as client:
        response = await client.post(url, headers=headers, data=data)
        res_data = response.json()

    if "tid" not in res_data:
        raise HTTPException(status_code=400, detail=f"KakaoPay Error: {res_data}")

    # DB 저장
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
    return payment


# --- 3. [이 부분이 없어서 404가 나는 겁니다!] ---
@router.get("/success")
async def payment_success_callback(pg_token: str):
    return HTMLResponse(content=f"""
    <html>
        <head><title>결제 성공</title></head>
        <body style="display:flex; flex-direction:column; align-items:center; justify-content:center; height:100vh;">
            <h1 style="color:green;">✅ 인증 성공!</h1>
            <p>아래 토큰을 복사해서 <b>/approve</b> API에 입력하세요.</p>
            <div style="background:#f0f0f0; padding:15px; border-radius:5px; font-weight:bold; font-size:1.2em;">
                {pg_token}
            </div>
        </body>
    </html>
    """)

@router.get("/cancel")
async def payment_cancel_callback():
    return {"message": "결제가 취소되었습니다."}

@router.get("/fail")
async def payment_fail_callback():
    return {"message": "결제에 실패했습니다."}