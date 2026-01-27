import httpx
import os
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import HTMLResponse, JSONResponse
from sqlalchemy.orm import Session
from datetime import datetime

# 데이터베이스 및 스키마 임포트
from ..database import get_db
from .. import models, schemas

# [Refactor 1] 배포 환경을 고려하여 기본 URL을 동적으로 설정
# .env 파일에 BASE_URL=https://my-server.com 처럼 설정하면 그게 적용되고, 없으면 로컬호스트가 됩니다.
BASE_URL = os.getenv("BASE_URL", "http://localhost:8000")
KAKAO_ADMIN_KEY = os.getenv("KAKAO_ADMIN_KEY")

router = APIRouter(
    prefix="/api/payments",
    tags=["payments"],
    responses={404: {"description": "Not found"}},
)

# --- 1. 결제 준비 (Ready) ---
@router.post(
    "/ready",
    response_model=schemas.PaymentReadyResponse,
    summary="결제 준비 요청 (TID 발급)",
    description="카카오페이 서버에 결제 요청을 보내고 TID(거래 고유 번호)를 발급받습니다."
)
async def payment_ready(
    request: schemas.PaymentReadyRequest,
    db: Session = Depends(get_db),
    user_id: int = 1  # TODO: 추후 Depends(get_current_user)로 변경하여 실제 로그인 유저 사용
):
    # 1. 카트 세션 확인
    cart_session = db.query(models.CartSession).filter(
        models.CartSession.cart_session_id == request.cart_session_id
    ).first()
    
    if not cart_session:
        raise HTTPException(status_code=404, detail="해당 카트 세션을 찾을 수 없습니다.")

    # 2. 기존 결제 시도 내역 정리 (중복 에러 방지)
    existing_payment = db.query(models.Payment).filter(
        models.Payment.cart_session_id == request.cart_session_id
    ).first()
    
    if existing_payment:
        db.delete(existing_payment)
        db.commit()

    # 3. 카카오페이 API 요청
    url = "https://kapi.kakao.com/v1/payment/ready"
    headers = {
        "Authorization": f"KakaoAK {KAKAO_ADMIN_KEY}",
        "Content-type": "application/x-www-form-urlencoded;charset=utf-8"
    }
    # [Refactor 1 적용] BASE_URL을 사용하여 주소 생성
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

    # 4. DB 저장 (PENDING)
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
@router.post(
    "/approve",
    response_model=schemas.PaymentResponse,
    summary="결제 승인 요청 (최종 완료)",
    description="사용자 인증 후 받은 pg_token으로 최종 결제 승인을 요청합니다."
)
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
    
    # 카트 세션 종료 처리
    cart_session = db.query(models.CartSession).filter(
        models.CartSession.cart_session_id == payment.cart_session_id
    ).first()
    
    if cart_session:
        cart_session.status = models.CartSessionStatus.PAID
        cart_session.ended_at = datetime.now()

    db.commit()
    db.refresh(payment)
    return payment


# --- 3. [문서화 반영] 콜백 URL (성공/취소/실패) ---

@router.get(
    "/success",
    response_class=HTMLResponse,
    summary="결제 성공 콜백 (리다이렉트)",
    description="카카오페이 인증 성공 시 이동하는 페이지입니다. pg_token을 반환합니다."
)
async def payment_success_callback(pg_token: str):
    """
    프론트엔드 연동 시:
    - 웹: 결제 완료 페이지로 리다이렉트 (pg_token 포함)
    - 앱: 딥링크 실행
    현재: 테스트용 HTML 반환
    """
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

@router.get(
    "/cancel",
    summary="결제 취소 콜백",
    description="사용자가 결제 화면에서 취소했을 때 이동하는 페이지입니다."
)
async def payment_cancel_callback():
    return JSONResponse(content={"message": "사용자가 결제를 취소했습니다.", "status": "CANCELLED"})

@router.get(
    "/fail",
    summary="결제 실패 콜백",
    description="결제 승인 실패(잔액 부족 등) 시 이동하는 페이지입니다."
)
async def payment_fail_callback():
    return JSONResponse(content={"message": "결제 승인에 실패했습니다.", "status": "FAILED"}, status_code=400)


# --- 4. [기능 추가] 상세 조회 ---
@router.get(
    "/{payment_id}", 
    response_model=schemas.PaymentDetailResponse,
    summary="결제 상세 조회",
    description="특정 결제 건의 상세 내역을 조회합니다."
)
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


# --- 5. [기능 추가] 결제 취소(환불) ---
@router.post(
    "/{payment_id}/cancel", 
    response_model=schemas.PaymentResponse,
    summary="결제 취소 (환불) 요청",
    description="승인 완료된 결제를 전액 취소합니다."
)
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

    # 카카오페이 API (취소)
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