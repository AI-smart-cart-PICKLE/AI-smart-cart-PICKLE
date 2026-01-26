import httpx
import os
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime

# 데이터베이스 및 스키마 임포트
from ..database import get_db
from .. import models, schemas
# from ..auth import get_current_user # (나중에 JWT Auth 구현 시 주석 해제)

router = APIRouter(
    prefix="/api/payments",
    tags=["payments"],
    responses={404: {"description": "Not found"}},
)

# 카카오페이 Admin Key (보안을 위해 환경변수 권장)
# .env 파일에 KAKAO_ADMIN_KEY=... 라고 적고 os.getenv로 불러오는 게 정석입니다.
KAKAO_ADMIN_KEY = os.getenv("KAKAO_ADMIN_KEY", "여기에_카카오_어드민_키_입력") 

# --- 결제 준비 (Ready) ---
@router.post("/ready", response_model=schemas.PaymentReadyResponse)
async def payment_ready(
    request: schemas.PaymentReadyRequest,
    db: Session = Depends(get_db),
    user_id: int = 1 # TODO: 추후 Depends(get_current_user)로 변경
):
    """
    1. 카트 세션을 확인하고
    2. 카카오페이에 결제 고유 번호(TID)를 요청한 뒤
    3. DB에 'PENDING(대기)' 상태로 저장합니다.
    """
    # 1. 카트 세션 존재 확인
    cart_session = db.query(models.CartSession).filter(
        models.CartSession.cart_session_id == request.cart_session_id
    ).first()
    
    if not cart_session:
        raise HTTPException(status_code=404, detail="해당 카트 세션을 찾을 수 없습니다.")

    # 2. 카카오페이 API 요청 준비
    url = "https://kapi.kakao.com/v1/payment/ready"
    headers = {
        "Authorization": f"KakaoAK {KAKAO_ADMIN_KEY}",
        "Content-type": "application/x-www-form-urlencoded;charset=utf-8"
    }
    
    # schemas.py에 정의된 total_amount를 그대로 사용
    data = {
        "cid": "TC0ONETIME", # 테스트용 가맹점 코드 (실제 계약 시 변경)
        "partner_order_id": str(cart_session.cart_session_id),
        "partner_user_id": str(user_id),
        "item_name": "Smart Cart Shopping", # 필요 시 '양파 외 3건' 처럼 동적 생성 가능
        "quantity": 1,
        "total_amount": request.total_amount,
        "tax_free_amount": 0,
        # 결제 성공/취소/실패 시 리다이렉트될 URL (프론트엔드 주소)
        "approval_url": "http://localhost:8000/api/payments/success_callback", 
        "cancel_url": "http://localhost:8000/api/payments/cancel_callback",
        "fail_url": "http://localhost:8000/api/payments/fail_callback",
    }

    # 3. 외부 API 통신 (httpx)
    async with httpx.AsyncClient() as client:
        response = await client.post(url, headers=headers, data=data)
        res_data = response.json()

    # 카카오페이 에러 처리
    if "tid" not in res_data:
        raise HTTPException(status_code=400, detail=f"KakaoPay Error: {res_data}")

    # 4. DB에 결제 정보 미리 저장 (PENDING) - ★매우 중요★
    # 승인 단계에서 검증하기 위해 미리 저장해둡니다.
    new_payment = models.Payment(
        cart_session_id=cart_session.cart_session_id,
        user_id=user_id,
        pg_provider=models.PgProviderType.KAKAO_PAY, # models.py의 Enum 사용
        pg_tid=res_data['tid'],
        status=models.PaymentStatus.PENDING,         # models.py의 Enum 사용
        total_amount=request.total_amount,
        method_id=request.method_id # 선택사항
    )
    db.add(new_payment)
    db.commit()

    # 5. 응답 반환 (schemas.PaymentReadyResponse 규격)
    return schemas.PaymentReadyResponse(
        tid=res_data['tid'],
        next_redirect_app_url=res_data['next_redirect_app_url'],
        next_redirect_mobile_url=res_data['next_redirect_mobile_url'],
        next_redirect_pc_url=res_data['next_redirect_pc_url']
    )


# --- 결제 승인 (Approve) ---
@router.post("/approve", response_model=schemas.PaymentResponse)
async def payment_approve(
    request: schemas.PaymentApproveRequest,
    db: Session = Depends(get_db),
    user_id: int = 1
):
    """
    사용자가 결제 비밀번호 입력을 완료하면 호출됩니다.
    최종적으로 결제를 승인하고 DB 상태를 업데이트합니다.
    """
    # 1. DB에서 아까 저장해둔 PENDING 상태의 결제 정보 찾기
    payment = db.query(models.Payment).filter(
        models.Payment.pg_tid == request.tid,
        models.Payment.user_id == user_id,
        models.Payment.status == models.PaymentStatus.PENDING
    ).first()

    if not payment:
        raise HTTPException(status_code=404, detail="대기 중인 결제 정보를 찾을 수 없습니다.")

    # 2. 카카오페이 승인 API 요청
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

    # 3. 승인 실패 처리
    if "aid" not in res_data:
        payment.status = models.PaymentStatus.FAILED
        db.commit()
        raise HTTPException(status_code=400, detail=f"Approval failed: {res_data}")

    # 4. 승인 성공 처리 (DB 업데이트)
    payment.status = models.PaymentStatus.APPROVED
    payment.approved_at = datetime.now()
    
    # 카트 세션 상태도 'PAID'로 변경하여 쇼핑 종료 처리
    cart_session = db.query(models.CartSession).filter(
        models.CartSession.cart_session_id == payment.cart_session_id
    ).first()
    
    if cart_session:
        cart_session.status = models.CartSessionStatus.PAID
        cart_session.ended_at = datetime.now()

    db.commit()
    db.refresh(payment) # 갱신된 데이터 불러오기
    
    return payment

# (선택) 결제 내역 조회 등 추가 기능은 필요할 때 구현할 것.