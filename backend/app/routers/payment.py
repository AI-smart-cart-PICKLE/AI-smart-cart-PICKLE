import httpx
import logging
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import HTMLResponse, JSONResponse
from sqlalchemy.orm import Session

# 로거 설정
logger = logging.getLogger(__name__)

# 내부 모듈 임포트
from .. import models, schemas, database
from ..dependencies import get_current_user, get_db
from app.utils.check_data import validate_cart_weight
from .ledger import create_ledger_from_payment
from app.core.config import settings

# 환경 변수 및 키 설정
BASE_URL = settings.BASE_URL
KAKAO_ADMIN_KEY = settings.KAKAO_ADMIN_KEY

# 라우터 설정
router = APIRouter(
    prefix="/payments",
    tags=["payments"],
    responses={404: {"description": "Not found"}},
)

# --- 카카오페이 CID 설정 ---
CID_ONETIME = "TC0ONETIME"       # 일반 결제
CID_SUBSCRIPTION = "TCSUBSCRIP"  # 정기/자동 결제


# =========================================================
# 🛠️ 헬퍼 함수 (중복 로직 분리)
# =========================================================

def get_payment_or_404(payment_id: int, user_id: int, db: Session):
    """결제 ID로 결제 내역 조회"""
    payment = db.query(models.Payment).filter(
        models.Payment.payment_id == payment_id,
        models.Payment.user_id == user_id
    ).first()
    
    if not payment:
        raise HTTPException(status_code=404, detail="결제 내역을 찾을 수 없습니다.")
    return payment

async def process_subscription_payment(
    db: Session,
    user: models.AppUser,
    cart_session_id: int,
    amount: int,
    item_name: str
):
    """
    ✅ [수정 3] 결제 실행 공통 로직 함수
    - request_payment와 pay_subscription에서 공통으로 사용합니다.
    """
    # 1. 빌링키 조회
    my_card = db.query(models.PaymentMethod).filter(
        models.PaymentMethod.user_id == user.user_id,
        models.PaymentMethod.billing_key.isnot(None)
    ).order_by(models.PaymentMethod.is_default.desc()).first()

    if not my_card:
        raise HTTPException(status_code=404, detail="등록된 자동결제 수단이 없습니다. 카드를 먼저 등록해주세요.")

    # 2. 카카오페이 결제 요청
    url = "https://kapi.kakao.com/v1/payment/subscription"
    headers = {
        "Authorization": f"KakaoAK {KAKAO_ADMIN_KEY}",
        "Content-type": "application/x-www-form-urlencoded;charset=utf-8"
    }

    partner_order_id = f"sub_{cart_session_id}_{int(datetime.now().timestamp())}"

    pay_data = {
        "cid": CID_SUBSCRIPTION,
        "sid": my_card.billing_key,
        "partner_order_id": partner_order_id,
        "partner_user_id": str(user.user_id),
        "item_name": item_name,
        "quantity": 1,
        "total_amount": amount,
        "tax_free_amount": 0,
    }

    async with httpx.AsyncClient() as client:
        response = await client.post(url, headers=headers, data=pay_data)
        res_data = response.json()

    if "tid" not in res_data:
        raise HTTPException(status_code=400, detail=f"결제 승인 실패: {res_data}")

    # 3. 결제 내역 저장 (Payment)
    new_payment = models.Payment(
        user_id=user.user_id,
        cart_session_id=cart_session_id,
        method_id=my_card.method_id,
        pg_provider=models.PgProviderType.KAKAO_PAY,
        pg_tid=res_data['tid'],
        status=models.PaymentStatus.APPROVED,
        total_amount=amount,
        approved_at=datetime.now()
    )
    db.add(new_payment)

    # 4. 장바구니 상태 업데이트 (ACTIVE -> PAID)
    # session 객체를 다시 조회해서 업데이트 (안전성 확보)
    cart_session = db.query(models.CartSession).filter(
        models.CartSession.cart_session_id == cart_session_id
    ).first()

    if cart_session:
        cart_session.status = models.CartSessionStatus.PAID
        cart_session.ended_at = datetime.now()

    db.commit()
    db.refresh(new_payment)

    # 5. 가계부 자동 등록
    try:
        create_ledger_from_payment(payment_id=new_payment.payment_id, db=db)
    except Exception as e:
        print(f"⚠️ 가계부 자동등록 실패: {e}")

    return {
        "status": "SUCCESS",
        "message": "결제가 완료되었습니다.",
        "amount": amount,
        "tid": res_data["tid"],
        "approved_at": res_data["approved_at"]
    }


# =========================================================
# 🛍️ [Main] 결제 요청 및 검증 (웹 프론트엔드 연동)
# =========================================================

@router.post("/request")
async def request_payment(
    req: schemas.PaymentRequest,
    db: Session = Depends(get_db),
    current_user: models.AppUser = Depends(get_current_user)
):
    """
    [결제 요청 API] 무게 검증 후 자동 결제를 수행합니다.
    """
    # 1. 세션 조회
    cart_session = db.query(models.CartSession).filter(
        models.CartSession.cart_session_id == req.cart_session_id,
        models.CartSession.user_id == current_user.user_id,
        models.CartSession.status == models.CartSessionStatus.ACTIVE
    ).first()

    if not cart_session:
        raise HTTPException(status_code=404, detail="결제할 활성 장바구니 세션을 찾을 수 없습니다.")

    # 2. 무게 업데이트 및 검증
    cart_session.measured_total_g = req.measured_weight_g
    db.commit()

    weight_check = validate_cart_weight(
        db=db,
        cart_session_id=req.cart_session_id,
        measured_weight_g=req.measured_weight_g
    )

    if not weight_check["is_valid"]:
        return JSONResponse(
            status_code=409,
            content={
                "status": "WARNING",
                "message": weight_check["message"],
                "difference": weight_check["difference"],
                "expected_weight": weight_check["expected_weight"],
                "measured_weight": weight_check["measured_weight"],
                "action_required": "CHECK_CART_ITEMS"
            }
        )

    # 3. 결제 진행 (자동결제)
    if req.use_subscription:
        try:
            # ♻️ 공통 함수 호출로 코드 중복 해결!
            return await process_subscription_payment(
                db=db,
                user=current_user,
                cart_session_id=req.cart_session_id,
                amount=req.amount,
                item_name="스마트 장바구니 결제"
            )
        except HTTPException as e:
            raise e
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"결제 오류: {str(e)}")
    else:
        return {"message": "일반 결제(QR)는 /ready API를 사용하세요."}


# =========================================================
# 🆕 정기결제(Billing Key) 등록 및 테스트 결제
# =========================================================

@router.post("/subscription/register/ready", response_model=schemas.PaymentReadyResponse)
async def register_card_ready(
    current_user: models.AppUser = Depends(get_current_user)
):
    """[카드 등록 1단계] 인증 요청"""
    url = "https://kapi.kakao.com/v1/payment/ready"
    headers = {
        "Authorization": f"KakaoAK {KAKAO_ADMIN_KEY}",
        "Content-type": "application/x-www-form-urlencoded;charset=utf-8"
    }

    order_id = f"reg_{current_user.user_id}_{int(datetime.now().timestamp())}"

    data = {
        "cid": CID_SUBSCRIPTION,
        "partner_order_id": order_id,
        "partner_user_id": str(current_user.user_id),
        "item_name": "카드 자동결제 등록",
        "quantity": 1,
        "total_amount": 0,
        "tax_free_amount": 0,
        "approval_url": f"{BASE_URL}/api/payments/subscription/register/callback?status=success",
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
        partner_order_id=order_id
    )


@router.get("/subscription/register/approve")
async def register_card_approve(
    tid: str,
    pg_token: str,
    partner_order_id: str,
    db: Session = Depends(get_db),
    current_user: models.AppUser = Depends(get_current_user)
):
    """[카드 등록 2단계] 빌링키 발급"""
    url = "https://kapi.kakao.com/v1/payment/approve"
    headers = {
        "Authorization": f"KakaoAK {KAKAO_ADMIN_KEY}",
        "Content-type": "application/x-www-form-urlencoded;charset=utf-8"
    }

    data = {
        "cid": CID_SUBSCRIPTION,
        "tid": tid,
        "partner_order_id": partner_order_id,
        "partner_user_id": str(current_user.user_id),
        "pg_token": pg_token
    }

    async with httpx.AsyncClient() as client:
        response = await client.post(url, headers=headers, data=data)
        res_data = response.json()

    if "sid" not in res_data:
        raise HTTPException(status_code=400, detail=f"등록 실패: {res_data}")

    sid = res_data["sid"]
    card_info = res_data.get("card_info", {})

    new_method = models.PaymentMethod(
        user_id=current_user.user_id,
        method_type=models.PaymentMethodType.KAKAO_PAY,
        billing_key=sid,
        card_brand=card_info.get("kakaopay_purchase_corp", "KAKAO"),
        card_last4=card_info.get("bin", "0000")[:4],
        is_default=True
    )

    db.add(new_method)
    db.commit()
    db.refresh(new_method)

    return {"message": "카드 등록 완료", "billing_key": sid, "method_id": new_method.method_id}


@router.post("/subscription/pay")
async def pay_subscription(
    cart_session_id: int,
    amount: int,
    item_name: str = "스마트 장바구니 자동결제",
    db: Session = Depends(get_db),
    current_user: models.AppUser = Depends(get_current_user)
):
    """
    [테스트용/직접호출용] 무게 검증 없이 즉시 결제
    """
    # ♻️ 공통 함수 호출로 코드 중복 해결!
    return await process_subscription_payment(
        db=db,
        user=current_user,
        cart_session_id=cart_session_id,
        amount=amount,
        item_name=item_name
    )


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
# 🚀 [Legacy] 일반 1회성 결제 (QR/PC)
# =========================================================
# (이하 1회성 결제 코드는 변경 없음, 그대로 유지하면 됩니다)
# ...
@router.post("/ready", response_model=schemas.PaymentReadyResponse)
async def payment_ready(
    request: schemas.PaymentReadyRequest,
    db: Session = Depends(get_db)
):
    """
    [결제 준비 API] 웹 키오스크에서도 호출 가능하도록 인증을 해제합니다.
    """
    cart_session = db.query(models.CartSession).filter(
        models.CartSession.cart_session_id == request.cart_session_id
    ).first()
    
    if not cart_session:
        raise HTTPException(status_code=404, detail="해당 카트 세션을 찾을 수 없습니다.")

    # 결제 주체 유저 ID 가져오기 (세션에 연결된 유저)
    user_id = cart_session.user_id
    if not user_id:
         raise HTTPException(status_code=400, detail="세션에 연결된 사용자가 없습니다.")

    # [무게 검증 로직 제거됨]

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
    
    # Append session_id to default URLs to identify the session in callback
    approval_url = request.approval_url or f"{BASE_URL}/api/payments/success?session_id={cart_session.cart_session_id}"
    cancel_url = request.cancel_url or f"{BASE_URL}/api/payments/cancel?session_id={cart_session.cart_session_id}"
    fail_url = request.fail_url or f"{BASE_URL}/api/payments/fail?session_id={cart_session.cart_session_id}"

    data = {
        "cid": CID_ONETIME,
        "partner_order_id": str(cart_session.cart_session_id),
        "partner_user_id": str(user_id),
        "item_name": "스마트 장보기 결제",
        "quantity": 1,
        "total_amount": request.total_amount,
        "tax_free_amount": 0,
        "approval_url": approval_url,
        "cancel_url": cancel_url,
        "fail_url": fail_url,
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

@router.get("/success", response_class=HTMLResponse)
async def payment_success_callback(
    pg_token: str, 
    session_id: int, 
    db: Session = Depends(get_db)
):
    """
    [웹 결제 콜백] 카카오페이 결제 성공 시 호출됩니다.
    여기서 직접 승인(Approve) 처리를 진행하여 세션을 종료시킵니다.
    """
    logger.info(f"🏁 콜백 수신 - Session ID: {session_id}, Token: {pg_token[:5]}...")

    # 1. 해당 세션의 대기 중인 결제 정보 조회 (최신 순으로 조회)
    payment = db.query(models.Payment).filter(
        models.Payment.cart_session_id == session_id,
        models.Payment.status == models.PaymentStatus.PENDING
    ).order_by(models.Payment.payment_id.desc()).first()

    if not payment:
        logger.error(f"❌ 결제 정보를 찾을 수 없음 - Session ID: {session_id}")
        # DB에 있는 해당 세션의 다른 결제 정보가 있는지 확인 (디버깅용)
        any_payment = db.query(models.Payment).filter(models.Payment.cart_session_id == session_id).first()
        status_msg = f" (상태: {any_payment.status if any_payment else '데이터없음'})"
        
        return HTMLResponse(content=f"""
            <div style="text-align:center; margin-top:50px;">
                <h1>❌ 결제 정보를 찾을 수 없습니다.</h1>
                <p>세션 번호: {session_id}{status_msg}</p>
                <p>관리자에게 문의해 주세요.</p>
            </div>
        """, status_code=404)

    # 2. 카카오페이 승인 API 호출
    url = "https://kapi.kakao.com/v1/payment/approve"
    headers = {
        "Authorization": f"KakaoAK {KAKAO_ADMIN_KEY}",
        "Content-type": "application/x-www-form-urlencoded;charset=utf-8"
    }
    
    # Ready 시점과 동일한 partner 정보 구성
    partner_order_id = str(payment.cart_session_id)
    partner_user_id = str(payment.user_id)
    
    data = {
        "cid": CID_ONETIME,
        "tid": payment.pg_tid,
        "partner_order_id": partner_order_id,
        "partner_user_id": partner_user_id,
        "pg_token": pg_token
    }

    logger.info(f"--- 카카오 승인 요청 시작 ---")
    logger.info(f"TID: {payment.pg_tid}, Session: {session_id}, User: {payment.user_id}")

    async with httpx.AsyncClient() as client:
        res = await client.post(url, headers=headers, data=data)
        res_data = res.json()

    logger.info(f"--- 카카오 승인 응답 결과 ---")
    logger.info(f"Response: {res_data}")

    if "aid" in res_data:
        # 3. 승인 성공 시 상태 업데이트
        payment.status = models.PaymentStatus.APPROVED
        payment.approved_at = datetime.now()
        
        cart_session = db.query(models.CartSession).filter(
            models.CartSession.cart_session_id == session_id
        ).first()
        if cart_session:
            cart_session.status = models.CartSessionStatus.PAID
            cart_session.ended_at = datetime.now()
            logger.info(f"✅ 결제 승인 완료 및 세션 종료 (Session ID: {session_id})")

        db.commit()
        
        # 가계부 등록
        try:
            create_ledger_from_payment(payment_id=payment.payment_id, db=db)
        except Exception as e:
            logger.error(f"⚠️ 가계부 등록 실패: {e}")

        return HTMLResponse(content="""
            <div style="display:flex; flex-direction:column; align-items:center; justify-content:center; height:100vh; font-family:sans-serif; background-color:#f8fafc;">
                <div style="background:white; padding:40px; border-radius:32px; box-shadow:0 20px 25px -5px rgba(0,0,0,0.1); text-align:center;">
                    <h1 style="color:#8b5cf6; font-size:48px; margin-bottom:16px;">✅</h1>
                    <h2 style="color:#1e293b; margin-bottom:8px;">결제가 완료되었습니다!</h2>
                    <p style="color:#64748b;">카카오톡으로 결제 알림이 전송되었습니다.</p>
                    <p style="color:#94a3b8; font-size:14px; margin-top:20px;">잠시 후 화면이 자동으로 닫힙니다.</p>
                </div>
            </div>
        """)
    
    error_msg = res_data.get('msg', '알 수 없는 오류')
    logger.error(f"❌ 카카오 결제 승인 실패: {error_msg}")
    return HTMLResponse(content=f"""
        <div style="text-align:center; margin-top:50px; font-family:sans-serif;">
            <h1 style="color:red;">❌ 결제 승인 실패</h1>
            <p>{error_msg}</p>
            <p>TID: {payment.pg_tid}</p>
        </div>
    """, status_code=400)

@router.get("/cancel")
async def payment_cancel_callback():
    return JSONResponse(content={"message": "결제 취소", "status": "CANCELLED"})

@router.get("/fail")
async def payment_fail_callback():
    return JSONResponse(content={"message": "결제 실패", "status": "FAILED"}, status_code=400)

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

    cid_to_use = CID_ONETIME if payment.method_id is None else CID_SUBSCRIPTION

    data = {
        "cid": cid_to_use,
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