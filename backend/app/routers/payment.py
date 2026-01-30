import httpx
import os
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.responses import HTMLResponse, JSONResponse
from sqlalchemy.orm import Session

# 내부 모듈 임포트
from .. import models, schemas, database
from ..dependencies import get_current_user, get_db
from app.utils.check_data import validate_cart_weight
from .ledger import create_ledger_from_payment

# 환경 변수 로드
BASE_URL = os.getenv("BASE_URL", "http://localhost:8000")
KAKAO_ADMIN_KEY = os.getenv("KAKAO_ADMIN_KEY")

# 라우터 설정
router = APIRouter(
    prefix="/api/payments",
    tags=["payments"],
    responses={404: {"description": "Resource Not found"}},
)


# --- 카카오페이 CID 설정 ---
# CID는 가맹점 코드입니다. 테스트용 코드를 사용합니다.
CID_ONETIME = "TC0ONETIME"       # 일반 결제 (1회성, QR/PC)
CID_SUBSCRIPTION = "TCSUBSCRIP"  # 정기/자동 결제 (빌링키 사용)


# =========================================================
# 🛠️ 헬퍼 함수 (내부 사용)
# =========================================================

def get_payment_or_404(payment_id: int, user_id: int, db: Session):
    """결제 ID로 결제 내역을 조회하고, 없으면 404 에러를 반환합니다."""
    payment = db.query(models.Payment).filter(
        models.Payment.payment_id == payment_id,
        models.Payment.user_id == user_id
    ).first()
    
    if not payment:
        raise HTTPException(status_code=404, detail="결제 내역을 찾을 수 없습니다.")
    return payment


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
    **[결제 요청 API] 웹에서 '결제하기' 버튼을 눌렀을 때 호출되는 핵심 엔드포인트입니다.**
    
    1. **무게 업데이트:** Jetson/센서가 측정한 무게(`measured_weight_g`)를 DB에 반영합니다.
    2. **무게 검증:** 예상 무게와 측정 무게를 비교합니다.
    3. **분기 처리:**
       - 🚨 **불일치 시:** 409 Conflict 상태코드와 함께 경고 메시지, 무게 차이 정보를 반환합니다. (프론트에서 팝업 띄움)
       - ✅ **일치 시:** `use_subscription=True`라면 즉시 자동 결제를 진행하고 결과를 반환합니다.
    """
    
    # 1. 활성 장바구니 세션 조회
    cart_session = db.query(models.CartSession).filter(
        models.CartSession.cart_session_id == req.cart_session_id,
        models.CartSession.user_id == current_user.user_id,
        models.CartSession.status == models.CartSessionStatus.ACTIVE
    ).first()

    if not cart_session:
        raise HTTPException(status_code=404, detail="결제할 활성 장바구니 세션을 찾을 수 없습니다.")

    # 2. 측정 무게 업데이트 (Jetson -> Web -> Server DB)
    # 결제 전 가장 최신 무게 상태를 기록합니다.
    cart_session.measured_total_g = req.measured_weight_g
    db.commit() 

    # 3. 무게 검증 로직 수행
    weight_check = validate_cart_weight(
        db=db,
        cart_session_id=req.cart_session_id,
        measured_weight_g=req.measured_weight_g
    )

    # 4. [검증 실패] 무게 불일치 -> 경고 응답 (409 Conflict)
    if not weight_check["is_valid"]:
        # 프론트엔드는 이 응답을 받으면 결제를 중단하고 '상품 점검 팝업'을 띄워야 합니다.
        return JSONResponse(
            status_code=409, 
            content={
                "status": "WARNING",
                "message": weight_check["message"], # 예: "무게가 200g 더 무겁습니다."
                "difference": weight_check["difference"],
                "expected_weight": weight_check["expected_weight"],
                "measured_weight": weight_check["measured_weight"],
                "action_required": "CHECK_CART_ITEMS" 
            }
        )

    # 5. [검증 성공] 무게 일치 -> 결제 진행
    # 사용자가 자동결제(구독) 방식을 사용하는 경우
    if req.use_subscription:
        # --- 내부 자동 결제 로직 시작 ---
        try:
            # 5-1. 등록된 빌링키(카드) 조회
            my_card = db.query(models.PaymentMethod).filter(
                models.PaymentMethod.user_id == current_user.user_id,
                models.PaymentMethod.billing_key.isnot(None)
            ).order_by(models.PaymentMethod.is_default.desc()).first()
            
            if not my_card:
                raise HTTPException(status_code=404, detail="등록된 자동결제 수단이 없습니다. 마이페이지에서 카드를 먼저 등록해주세요.")

            # 5-2. 카카오페이 정기결제 API 호출
            url = "https://kapi.kakao.com/v1/payment/subscription"
            headers = {
                "Authorization": f"KakaoAK {KAKAO_ADMIN_KEY}",
                "Content-type": "application/x-www-form-urlencoded;charset=utf-8"
            }
            
            # 주문번호에 세션ID와 타임스탬프를 조합해 유니크하게 생성
            partner_order_id = f"sub_{req.cart_session_id}_{int(datetime.now().timestamp())}"

            pay_data = {
                "cid": CID_SUBSCRIPTION,
                "sid": my_card.billing_key, # 저장된 빌링키 사용
                "partner_order_id": partner_order_id,
                "partner_user_id": str(current_user.user_id),
                "item_name": "스마트 장바구니 결제",
                "quantity": 1,
                "total_amount": req.amount,
                "tax_free_amount": 0,
            }
            
            async with httpx.AsyncClient() as client:
                response = await client.post(url, headers=headers, data=pay_data)
                res_data = response.json()
                
            if "tid" not in res_data:
                # 카카오페이 측 에러 (잔액 부족, 한도 초과 등)
                raise HTTPException(status_code=400, detail=f"결제 승인 실패: {res_data}")

            # 5-3. 결제 성공 처리
            # (1) Payment 내역 저장
            new_payment = models.Payment(
                user_id=current_user.user_id,
                cart_session_id=req.cart_session_id,
                method_id=my_card.method_id,
                pg_provider=models.PgProviderType.KAKAO_PAY,
                pg_tid=res_data['tid'],
                status=models.PaymentStatus.APPROVED,
                total_amount=req.amount,
                approved_at=datetime.now()
            )
            db.add(new_payment)
            
            # (2) 장바구니 세션 종료 (ACTIVE -> PAID)
            cart_session.status = models.CartSessionStatus.PAID
            cart_session.ended_at = datetime.now()
            
            db.commit()
            db.refresh(new_payment)
            
            # (3) 가계부 자동 등록 (실패해도 결제는 성공으로 처리)
            try:
                create_ledger_from_payment(payment_id=new_payment.payment_id, db=db)
            except Exception as e:
                print(f"⚠️ 가계부 자동등록 실패: {e}")

            return {
                "status": "SUCCESS",
                "message": "결제가 완료되었습니다.",
                "amount": req.amount,
                "tid": res_data["tid"],
                "approved_at": res_data["approved_at"]
            }

        except HTTPException as e:
            raise e
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"결제 처리 중 서버 오류 발생: {str(e)}")

    else:
        # 자동결제를 원치 않는 경우 (예: 현장 QR 결제 등)
        return {"message": "일반 결제(QR) 로직은 /ready API를 사용해주세요."}


# =========================================================
# 🆕 [설정] 정기결제(Billing Key) 등록 프로세스
# =========================================================

# --- 1. 카드 등록 준비 (인증 요청) ---
@router.post("/subscription/register/ready", response_model=schemas.PaymentReadyResponse)
async def register_card_ready(
    current_user: models.AppUser = Depends(get_current_user)
):
    """
    **[카드 등록 1단계]** 카카오페이에 '카드 등록(0원 결제)'을 요청하여 인증 URL을 받아옵니다.
    - 반환된 `partner_order_id`는 2단계(approve)에서 반드시 동일하게 사용해야 합니다.
    """
    url = "https://kapi.kakao.com/v1/payment/ready"
    headers = {
        "Authorization": f"KakaoAK {KAKAO_ADMIN_KEY}",
        "Content-type": "application/x-www-form-urlencoded;charset=utf-8"
    }
    
    # 주문번호 생성 (이 값을 기억해야 함!)
    order_id = f"reg_{current_user.user_id}_{int(datetime.now().timestamp())}"
    
    data = {
        "cid": CID_SUBSCRIPTION,  # 정기결제용 CID
        "partner_order_id": order_id,
        "partner_user_id": str(current_user.user_id),
        "item_name": "카드 자동결제 등록",
        "quantity": 1,
        "total_amount": 0,    # 인증용이라 0원
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
        partner_order_id=order_id # 클라이언트가 이 값을 저장해뒀다가 approve 때 보내줘야 함
    )


# --- 2. 카드 등록 승인 (Billing Key 발급) ---
@router.get("/subscription/register/approve")
async def register_card_approve(
    tid: str,
    pg_token: str,
    partner_order_id: str,
    db: Session = Depends(get_db),
    current_user: models.AppUser = Depends(get_current_user)
):
    """
    **[카드 등록 2단계]** 사용자가 카톡 인증을 마치면 받은 pg_token으로 빌링키(SID)를 발급받습니다.
    - 발급받은 `billing_key`는 DB(`payment_method`)에 암호화 저장되어 추후 결제에 사용됩니다.
    """
    url = "https://kapi.kakao.com/v1/payment/approve"
    headers = {
        "Authorization": f"KakaoAK {KAKAO_ADMIN_KEY}",
        "Content-type": "application/x-www-form-urlencoded;charset=utf-8"
    }
    
    data = {
        "cid": CID_SUBSCRIPTION,
        "tid": tid,
        "partner_order_id": partner_order_id, # 1단계의 그 ID여야 함
        "partner_user_id": str(current_user.user_id),
        "pg_token": pg_token
    }
    
    async with httpx.AsyncClient() as client:
        response = await client.post(url, headers=headers, data=data)
        res_data = response.json()

    if "sid" not in res_data:
        raise HTTPException(status_code=400, detail=f"등록 실패 (주문번호 불일치 등): {res_data}")

    # SID(Billing Key) 저장
    sid = res_data["sid"]
    card_info = res_data.get("card_info", {})
    
    # 기존 등록된 같은 카드가 있으면 업데이트, 없으면 생성
    new_method = models.PaymentMethod(
        user_id=current_user.user_id,
        method_type=models.PaymentMethodType.KAKAO_PAY,
        billing_key=sid,  # ★ 핵심: 이 키가 있어야 돈을 뺄 수 있음
        card_brand=card_info.get("kakaopay_purchase_corp", "KAKAO"),
        card_last4=card_info.get("bin", "0000")[:4], 
        is_default=True 
    )
    
    db.add(new_method)
    db.commit()
    db.refresh(new_method)

    return {"message": "카드 등록 완료", "billing_key": sid, "method_id": new_method.method_id}


# --- 3. 단순 자동 결제 (테스트용) ---
@router.post("/subscription/pay")
async def pay_subscription(
    cart_session_id: int,
    amount: int,
    item_name: str = "스마트 장바구니 자동결제",
    db: Session = Depends(get_db),
    current_user: models.AppUser = Depends(get_current_user)
):
    """
    **[테스트용/직접호출용]** 무게 검증 로직 없이 즉시 결제를 수행합니다.
    - 실제 서비스에서는 `/request` 엔드포인트를 사용하는 것을 권장합니다.
    """
    # 0. 세션 확인
    cart_session = db.query(models.CartSession).filter(
        models.CartSession.cart_session_id == cart_session_id,
        models.CartSession.user_id == current_user.user_id,
        models.CartSession.status == models.CartSessionStatus.ACTIVE
    ).first()

    if not cart_session:
        raise HTTPException(status_code=404, detail="결제할 활성 장바구니 세션이 없습니다.")

    # 1. 빌링키 조회
    my_card = db.query(models.PaymentMethod).filter(
        models.PaymentMethod.user_id == current_user.user_id,
        models.PaymentMethod.billing_key.isnot(None)
    ).order_by(models.PaymentMethod.is_default.desc()).first()
    
    if not my_card:
        raise HTTPException(status_code=404, detail="등록된 자동결제 수단이 없습니다.")

    # 2. 카카오페이 요청
    url = "https://kapi.kakao.com/v1/payment/subscription"
    headers = {
        "Authorization": f"KakaoAK {KAKAO_ADMIN_KEY}",
        "Content-type": "application/x-www-form-urlencoded;charset=utf-8"
    }
    
    data = {
        "cid": CID_SUBSCRIPTION,
        "sid": my_card.billing_key,
        "partner_order_id": f"sub_{cart_session_id}_{int(datetime.now().timestamp())}",
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

    # 3. DB 저장 및 상태 업데이트
    new_payment = models.Payment(
        user_id=current_user.user_id,
        cart_session_id=cart_session_id,
        method_id=my_card.method_id,
        pg_provider=models.PgProviderType.KAKAO_PAY,
        pg_tid=res_data['tid'],
        status=models.PaymentStatus.APPROVED,
        total_amount=amount,
        approved_at=datetime.now()
    )
    db.add(new_payment)
    
    cart_session.status = models.CartSessionStatus.PAID
    cart_session.ended_at = datetime.now()
    
    db.commit()
    db.refresh(new_payment)
    
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
    """카카오톡 인증 후 리다이렉트되는 페이지입니다. 토큰을 보여줍니다."""
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

@router.post("/ready", response_model=schemas.PaymentReadyResponse)
async def payment_ready(
    request: schemas.PaymentReadyRequest,
    db: Session = Depends(get_db),
    current_user: models.AppUser = Depends(get_current_user)
):
    """
    [일반 결제] 1회성 결제 요청입니다. (카카오톡 QR코드 스캔 방식)
    """
    user_id = current_user.user_id

    cart_session = db.query(models.CartSession).filter(
        models.CartSession.cart_session_id == request.cart_session_id
    ).first()
    
    if not cart_session:
        raise HTTPException(status_code=404, detail="해당 카트 세션을 찾을 수 없습니다.")

    # 무게 검증 (일반 결제도 검증 필수)
    weight_check = validate_cart_weight(
        db=db,
        cart_session_id=cart_session.cart_session_id,
        measured_weight_g=cart_session.measured_total_g
    )

    if not weight_check["is_valid"]:
        raise HTTPException(status_code=400, detail=weight_check["message"])

    # 기존 미완료 결제 내역 정리
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
        "cid": CID_ONETIME,  # ★ 1회성 CID
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


@router.post("/approve", response_model=schemas.PaymentResponse)
async def payment_approve(
    request: schemas.PaymentApproveRequest,
    db: Session = Depends(get_db),
    current_user: models.AppUser = Depends(get_current_user)
):
    """
    [일반 결제] 사용자가 QR 승인 후, TID와 pg_token으로 최종 승인 요청
    """
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
        "cid": CID_ONETIME,
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
    
    # 장바구니 상태 업데이트
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

# --- 콜백 URL들 ---
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
# 📦 CRUD 및 관리 기능 (결제 수단, 조회, 취소)
# ========================================================

@router.get("/methods", response_model=list[schemas.PaymentMethodResponse])
async def get_payment_methods(
    db: Session = Depends(get_db),
    current_user: models.AppUser = Depends(get_current_user)
):
    """등록된 결제 수단 목록 조회"""
    return db.query(models.PaymentMethod).filter(
        models.PaymentMethod.user_id == current_user.user_id
    ).all()


@router.post("/methods", response_model=schemas.PaymentMethodResponse)
async def register_payment_method(
    request: schemas.PaymentMethodCreate,
    db: Session = Depends(get_db),
    current_user: models.AppUser = Depends(get_current_user)
):
    """[테스트용] 결제 수단 수동 등록 (빌링키 직접 입력)"""
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
    """결제 수단 삭제"""
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
    """결제 상세 내역 조회"""
    return get_payment_or_404(payment_id, current_user.user_id, db)


@router.post("/{payment_id}/cancel", response_model=schemas.PaymentResponse)
async def cancel_payment(
    payment_id: int,
    request: schemas.PaymentCancelRequest,
    db: Session = Depends(get_db),
    current_user: models.AppUser = Depends(get_current_user)
):
    """
    결제 취소 요청 (전액 취소)
    - 카카오페이 API를 통해 실제 환불 처리를 진행합니다.
    """
    payment = get_payment_or_404(payment_id, current_user.user_id, db)

    if payment.status != models.PaymentStatus.APPROVED:
        raise HTTPException(status_code=400, detail="승인 완료된 결제만 취소할 수 있습니다.")

    url = "https://kapi.kakao.com/v1/payment/cancel"
    headers = {
        "Authorization": f"KakaoAK {KAKAO_ADMIN_KEY}",
        "Content-type": "application/x-www-form-urlencoded;charset=utf-8"
    }
    
    # 결제 방식(정기/일반)에 따라 CID가 다를 수 있음
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