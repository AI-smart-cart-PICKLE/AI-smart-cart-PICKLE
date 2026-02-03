import httpx
import os
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import HTMLResponse, JSONResponse
from sqlalchemy.orm import Session
from datetime import datetime
from .ledger import create_ledger_from_payment

from ..database import get_db
from .. import models, schemas
from ..dependencies import get_current_user 

BASE_URL = os.getenv("BASE_URL", "http://localhost:8000")
KAKAO_ADMIN_KEY = os.getenv("KAKAO_ADMIN_KEY")

router = APIRouter(
    prefix="/payments",
    tags=["payments"],
    responses={404: {"description": "Not found"}},
)

# =========================================================
# 🛠️ 헬퍼 함수
# =========================================================

def get_payment_or_404(payment_id: int, user_id: int, db: Session):
    payment = db.query(models.Payment).filter(
        models.Payment.payment_id == payment_id,
        models.Payment.user_id == user_id
    ).first()
    
    if not payment:
        raise HTTPException(status_code=404, detail="결제 내역을 찾을 수 없습니다.")
    return payment

# =========================================================
# 🚀 API 엔드포인트 (Auth 적용 완료)
# =========================================================

# --- 1. 결제 준비 (Ready) ---
@router.post("/ready", response_model=schemas.PaymentReadyResponse)
async def payment_ready(
    request: schemas.PaymentReadyRequest,
    db: Session = Depends(get_db),
    current_user: models.AppUser = Depends(get_current_user) # 👈 로그인 유저 주입
):
    # 이제 current_user.user_id 로 진짜 ID를 사용합니다.
    user_id = current_user.user_id

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
        "partner_user_id": str(user_id), # 진짜 유저 ID 사용
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
        user_id=user_id, # 진짜 유저 ID 저장
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
    current_user: models.AppUser = Depends(get_current_user) # 👈 로그인 유저
):
    user_id = current_user.user_id

    payment = db.query(models.Payment).filter(
        models.Payment.pg_tid == request.tid,
        models.Payment.user_id == user_id, # 본인 결제만 승인 가능
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
# 🚨 [라우팅 순서] 구체적인 경로가 위로!
# ========================================================

# --- 6. 결제 수단 목록 조회 ---
@router.get("/methods", response_model=list[schemas.PaymentMethodResponse])
async def get_payment_methods(
    db: Session = Depends(get_db),
    current_user: models.AppUser = Depends(get_current_user) # 👈 로그인 유저
):
    return db.query(models.PaymentMethod).filter(
        models.PaymentMethod.user_id == current_user.user_id
    ).all()


# --- 7. 결제 수단 등록 ---
@router.post("/methods", response_model=schemas.PaymentMethodResponse)
async def register_payment_method(
    request: schemas.PaymentMethodCreate,
    db: Session = Depends(get_db),
    current_user: models.AppUser = Depends(get_current_user) # 👈 로그인 유저
):
    user_id = current_user.user_id
    
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
    current_user: models.AppUser = Depends(get_current_user) # 👈 로그인 유저
):
    method = db.query(models.PaymentMethod).filter(
        models.PaymentMethod.method_id == method_id,
        models.PaymentMethod.user_id == current_user.user_id # 본인 카드만 삭제 가능
    ).first()

    if not method:
        raise HTTPException(status_code=404, detail="결제 수단을 찾을 수 없습니다.")

    db.delete(method)
    db.commit()
    return {"message": "결제 수단이 삭제되었습니다."}


# ========================================================
# 👇 상세 조회 및 취소
# ========================================================

# --- 4. 결제 상세 조회 ---
@router.get("/{payment_id}", response_model=schemas.PaymentDetailResponse)
async def get_payment_detail(
    payment_id: int,
    db: Session = Depends(get_db),
    current_user: models.AppUser = Depends(get_current_user) # 👈 로그인 유저
):
    # 본인 결제 내역만 조회 가능
    payment = get_payment_or_404(payment_id, current_user.user_id, db)
    
    # Pydantic 모델로 변환 (기본 필드)
    response = schemas.PaymentDetailResponse.model_validate(payment)
    
    # 아이템 목록 채우기 (CartSession -> items)
    if payment.session and payment.session.items:
        items_list = []
        for item in payment.session.items:
            # CartItemResponse 구조에 맞게 변환
            # item.product가 Lazy Loading 될 수 있으므로 접근
            product_simple = schemas.ProductSimpleResponse.model_validate(item.product)
            
            cart_item_res = schemas.CartItemResponse(
                cart_item_id=item.cart_item_id,
                product=product_simple,
                quantity=item.quantity,
                unit_price=item.unit_price,
                total_price=item.unit_price * item.quantity
            )
            items_list.append(cart_item_res)
        
        response.items = items_list
        
    return response


# --- 5. 결제 취소(환불) ---
@router.post("/{payment_id}/cancel", response_model=schemas.PaymentResponse)
async def cancel_payment(
    payment_id: int,
    request: schemas.PaymentCancelRequest,
    db: Session = Depends(get_db),
    current_user: models.AppUser = Depends(get_current_user) # 👈 로그인 유저
):
    payment = get_payment_or_404(payment_id, current_user.user_id, db)

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