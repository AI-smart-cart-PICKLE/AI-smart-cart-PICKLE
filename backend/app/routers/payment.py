import httpx
import os
from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.responses import HTMLResponse, JSONResponse
from sqlalchemy.orm import Session
from datetime import datetime
from .ledger import create_ledger_from_payment

from ..database import get_db
from .. import models, schemas
from ..dependencies import get_current_user 
from app.utils.check_data import validate_cart_weight


BASE_URL = os.getenv("BASE_URL", "http://localhost:8000")
KAKAO_ADMIN_KEY = os.getenv("KAKAO_ADMIN_KEY")

router = APIRouter(
    prefix="/api/payments",
    tags=["payments"],
    responses={404: {"description": "Not found"}},
)

# --- 카카오페이 CID 설정 ---
CID_ONETIME = "TC0ONETIME"       # 일반 결제 (기존)
CID_SUBSCRIPTION = "TCSUBSCRIP"  # 정기/자동 결제 (신규 추가)


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
# 🆕 [신규] 정기결제(Billing Key) 등록 및 사용
# =========================================================

# --- 1. 카드 등록 준비 (인증 요청) ---
@router.post("/subscription/register/ready", response_model=schemas.PaymentReadyResponse)
async def register_card_ready(
    current_user: models.AppUser = Depends(get_current_user)
):
    """
    [카드 등록 1단계] 카카오페이에 '나 카드 등록할래(0원)' 요청을 보냅니다.
    """
    url = "https://kapi.kakao.com/v1/payment/ready"
    headers = {
        "Authorization": f"KakaoAK {KAKAO_ADMIN_KEY}",
        "Content-type": "application/x-www-form-urlencoded;charset=utf-8"
    }
    
    # 주문번호 생성 (등록용)
    order_id = f"reg_{current_user.user_id}_{int(datetime.now().timestamp())}"
    
    data = {
        "cid": CID_SUBSCRIPTION,  # ★ 정기결제용 CID
        "partner_order_id": order_id,
        "partner_user_id": str(current_user.user_id),
        "item_name": "카드 자동결제 등록",
        "quantity": 1,
        "total_amount": 0,    # 등록 인증용이라 0원
        "tax_free_amount": 0,
        "approval_url": f"{BASE_URL}/api/payments/subscription/register/callback?status=success", # 콜백 분리
        "cancel_url": f"{BASE_URL}/api/payments/subscription/register/callback?status=cancel",
        "fail_url": f"{BASE_URL}/api/payments/subscription/register/callback?status=fail",
    }

    async with httpx.AsyncClient() as client:
        response = await client.post(url, headers=headers, data=data)
        res_data = response.json()

    if "tid" not in res_data:
        raise HTTPException(status_code=400, detail=f"KakaoPay Error: {res_data}")

    return schemas.PaymentReadyResponse(
        tid=res_data['tid'],
        next_redirect_app_url=res_data.get('next_redirect_app_url'),
        next_redirect_mobile_url=res_data.get('next_redirect_mobile_url'),
        next_redirect_pc_url=res_data.get('next_redirect_pc_url'),
        partner_order_id=order_id # 👈 복사할 수 있게 전달
    )
    # 주의: 실무에서는 여기서 TID와 order_id를 Redis나 DB에 임시 저장해야 승인 단계에서 검증 가능
    
    return schemas.PaymentReadyResponse(
        tid=res_data['tid'],
        next_redirect_app_url=res_data.get('next_redirect_app_url'),
        next_redirect_mobile_url=res_data.get('next_redirect_mobile_url'),
        next_redirect_pc_url=res_data.get('next_redirect_pc_url')
    )


# --- 2. 카드 등록 승인 (Billing Key 발급) ---
# 사용자가 카톡 인증 후 돌아오는 콜백용 API는 별도로 만들거나 approve에서 처리합니다.
# 여기서는 편의상 Swagger에서 직접 호출하는 approve API를 만듭니다.

@router.get("/subscription/register/approve")
async def register_card_approve(
    tid: str,
    pg_token: str,
    partner_order_id: str,
    db: Session = Depends(get_db),
    current_user: models.AppUser = Depends(get_current_user)
):
    """
    [카드 등록 2단계] pg_token을 받아 SID(Billing Key)를 발급받고 DB에 저장합니다.
    """
    url = "https://kapi.kakao.com/v1/payment/approve"
    headers = {
        "Authorization": f"KakaoAK {KAKAO_ADMIN_KEY}",
        "Content-type": "application/x-www-form-urlencoded;charset=utf-8"
    }
    
    # 원래는 ready 단계의 partner_order_id를 가져와야 합니다. 
    # 편의상 user_id 기반으로 비슷하게 매칭하거나 테스트용 값 사용
    
    data = {
        "cid": CID_SUBSCRIPTION,
        "tid": tid,
        "partner_order_id": partner_order_id, # 테스트 시 주의 (에러나면 ready시 쓴 값 필요)
        "partner_user_id": str(current_user.user_id),
        "pg_token": pg_token
    }
    
    # *참고: partner_order_id가 ready때와 다르면 카카오에서 에러를 뱉습니다.
    # 실무에선 Redis에 저장하지만, 테스트 단계에선 ready 요청시 보낸 order_id를 기억했다가 넣어야 할 수 있습니다.
    # 여기서는 에러 방지를 위해, ready 함수 내의 order_id 생성 규칙을 클라이언트가 파라미터로 주거나
    # DB에 잠시 저장하는 로직이 필요합니다. (일단 단순화하여 진행)

    async with httpx.AsyncClient() as client:
        response = await client.post(url, headers=headers, data=data)
        res_data = response.json()

    if "sid" not in res_data:
         # partner_order_id 불일치 등의 에러 처리
        raise HTTPException(status_code=400, detail=f"등록 실패 (주문번호 불일치 등): {res_data}")

    # ★ 핵심: SID(Billing Key) 저장
    sid = res_data["sid"]
    card_info = res_data.get("card_info", {})
    
    # 기존 등록된 같은 카드가 있으면 업데이트, 없으면 생성
    new_method = models.PaymentMethod(
        user_id=current_user.user_id,
        method_type=models.PaymentMethodType.KAKAO_PAY,
        billing_key=sid,  # 이 키가 있어야 자동결제 가능
        card_brand=card_info.get("kakaopay_purchase_corp", "KAKAO"),
        card_last4=card_info.get("bin", "0000")[:4], 
        is_default=True 
    )
    
    db.add(new_method)
    db.commit()
    db.refresh(new_method)

    return {"message": "카드 등록 완료", "billing_key": sid, "method_id": new_method.method_id}


# --- 3. [핵심] 자동 결제 (SID 사용) ---
@router.post("/subscription/pay")
async def pay_subscription(
    amount: int,
    item_name: str = "스마트 장바구니 자동결제",
    db: Session = Depends(get_db),
    current_user: models.AppUser = Depends(get_current_user)
):
    """
    [자동 결제] 비밀번호 입력 없이 저장된 키(SID)로 즉시 결제합니다.
    """
    # 1. 내 빌링키 조회
    my_card = db.query(models.PaymentMethod).filter(
        models.PaymentMethod.user_id == current_user.user_id,
        models.PaymentMethod.billing_key.isnot(None)
    ).order_by(models.PaymentMethod.is_default.desc()).first()
    
    if not my_card:
        raise HTTPException(status_code=404, detail="등록된 자동결제 수단이 없습니다.")

    # 2. 카카오페이 정기결제 요청
    url = "https://kapi.kakao.com/v1/payment/subscription"
    headers = {
        "Authorization": f"KakaoAK {KAKAO_ADMIN_KEY}",
        "Content-type": "application/x-www-form-urlencoded;charset=utf-8"
    }
    
    data = {
        "cid": CID_SUBSCRIPTION,
        "sid": my_card.billing_key, # 저장된 키 사용
        "partner_order_id": f"sub_{int(datetime.now().timestamp())}",
        "partner_user_id": str(current_user.user_id),
        "item_name": item_name,
        "quantity": 1,
        "total_amount": amount,
        "tax_free_amount": 0,
    }
    
    async with httpx.AsyncClient() as client:
        response = await client.post(url, headers=headers, data=data)
        res_data = response.json()
        
    if "tid" not in res_data:
         raise HTTPException(status_code=400, detail=f"자동 결제 실패: {res_data}")

    # 3. 결제 정보 저장 (Payment 테이블)
    new_payment = models.Payment(
        user_id=current_user.user_id,
        # cart_session_id는 필수가 아닐 수 있으므로 상황에 따라 처리 (여기선 NULL 허용 가정)
        method_id=my_card.method_id,
        pg_provider=models.PgProviderType.KAKAO_PAY,
        pg_tid=res_data['tid'],
        status=models.PaymentStatus.APPROVED, # 자동결제는 바로 승인됨
        total_amount=amount,
        approved_at=datetime.now()
    )
    db.add(new_payment)
    db.commit()
    db.refresh(new_payment)
    
    # 4. 가계부 자동 등록
    try:
        create_ledger_from_payment(payment_id=new_payment.payment_id, db=db)
    except Exception as e:
        print(f"가계부 등록 오류: {e}")

    return {
        "status": "SUCCESS",
        "amount": amount,
        "tid": res_data["tid"],
        "approved_at": res_data["approved_at"]
    }

# --- 카드 등록용 콜백 (HTML) ---
@router.get("/subscription/register/callback", response_class=HTMLResponse)
async def register_callback(status: str, pg_token: str = None):
    if status == "success":
        return f"""
        <html>
            <head><title>등록 성공</title></head>
            <body>
                <h1 style="color:blue;">카드 등록 인증 완료!</h1>
                <p>아래 토큰을 복사해서 <b>approve API</b>에 입력하세요.</p>
                <div style="background:#eee; padding:10px; font-size:1.2em;">{pg_token}</div>
            </body>
        </html>
        """
    return "<h1>등록 취소 또는 실패</h1>"


# =========================================================
# 🚀 기존 API 엔드포인트 (1회성 결제 유지)
# =========================================================

# --- 1. 결제 준비 (Ready) - 기존 유지 ---
@router.post("/ready", response_model=schemas.PaymentReadyResponse)
async def payment_ready(
    request: schemas.PaymentReadyRequest,
    db: Session = Depends(get_db),
    current_user: models.AppUser = Depends(get_current_user)
):
    # ... (기존 코드와 동일, CID_ONETIME 사용) ...
    user_id = current_user.user_id

    cart_session = db.query(models.CartSession).filter(
        models.CartSession.cart_session_id == request.cart_session_id
    ).first()
    
    if not cart_session:
        raise HTTPException(status_code=404, detail="해당 카트 세션을 찾을 수 없습니다.")

    # 무게 검증
    weight_check = validate_cart_weight(
        db=db,
        cart_session_id=cart_session.cart_session_id,
        measured_weight_g=cart_session.measured_total_g
    )

    if not weight_check["is_valid"]:
        # 무게 초과 / 부족에 맞는 메시지 그대로 반환
        raise HTTPException(
            status_code=400,
            detail=weight_check["message"]
        )

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
        "cid": CID_ONETIME,  # ★ 기존 1회성 CID
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


# --- 2. 결제 승인 (Approve) - 기존 유지 ---
@router.post("/approve", response_model=schemas.PaymentResponse)
async def payment_approve(
    request: schemas.PaymentApproveRequest,
    db: Session = Depends(get_db),
    current_user: models.AppUser = Depends(get_current_user)
):
    # ... (기존 로직 유지) ...
    user_id = current_user.user_id

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
        "cid": CID_ONETIME, # ★ 기존 1회성 CID
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
    
    # 카트 세션 상태 업데이트
    if payment.cart_session_id:
        cart_session = db.query(models.CartSession).filter(
            models.CartSession.cart_session_id == payment.cart_session_id
        ).first()
        if cart_session:
            cart_session.status = models.CartSessionStatus.PAID
            cart_session.ended_at = datetime.now()

    db.commit()
    db.refresh(payment)

    # 가계부 연동
    try:
        create_ledger_from_payment(payment_id=payment.payment_id, db=db)
    except Exception as e:
        print(f"⚠️ 가계부 등록 실패: {e}")

    return payment

# --- 콜백 URL들 (success, cancel, fail) ---
@router.get("/success", response_class=HTMLResponse)
async def payment_success_callback(pg_token: str):
    return HTMLResponse(content=f"""
    <html>
        <head><title>결제 성공</title></head>
        <body style="display:flex; flex-direction:column; align-items:center; justify-content:center; height:100vh;">
            <h1 style="color:green;">✅ 결제 승인 대기중</h1>
            <p>앱으로 돌아가서 결제 완료 버튼을 눌러주세요.</p>
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
# CRUD 및 기타 기능들
# ========================================================

@router.get("/methods", response_model=list[schemas.PaymentMethodResponse])
async def get_payment_methods(
    db: Session = Depends(get_db),
    current_user: models.AppUser = Depends(get_current_user)
):
    return db.query(models.PaymentMethod).filter(
        models.PaymentMethod.user_id == current_user.user_id
    ).all()


@router.post("/methods", response_model=schemas.PaymentMethodResponse)
async def register_payment_method(
    request: schemas.PaymentMethodCreate,
    db: Session = Depends(get_db),
    current_user: models.AppUser = Depends(get_current_user)
):
    # 기존 수동 등록 로직 유지 (테스트용)
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


@router.delete("/methods/{method_id}")
async def delete_payment_method(
    method_id: int,
    db: Session = Depends(get_db),
    current_user: models.AppUser = Depends(get_current_user)
):
    method = db.query(models.PaymentMethod).filter(
        models.PaymentMethod.method_id == method_id,
        models.PaymentMethod.user_id == current_user.user_id
    ).first()

    if not method:
        raise HTTPException(status_code=404, detail="결제 수단을 찾을 수 없습니다.")

    db.delete(method)
    db.commit()
    return {"message": "결제 수단이 삭제되었습니다."}


@router.get("/{payment_id}", response_model=schemas.PaymentDetailResponse)
async def get_payment_detail(
    payment_id: int,
    db: Session = Depends(get_db),
    current_user: models.AppUser = Depends(get_current_user)
):
    return get_payment_or_404(payment_id, current_user.user_id, db)


@router.post("/{payment_id}/cancel", response_model=schemas.PaymentResponse)
async def cancel_payment(
    payment_id: int,
    request: schemas.PaymentCancelRequest,
    db: Session = Depends(get_db),
    current_user: models.AppUser = Depends(get_current_user)
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
        "cid": CID_ONETIME if payment.method_id is None else CID_SUBSCRIPTION, # 결제 방식에 따라 CID 변경 필요
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