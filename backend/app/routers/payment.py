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
from ..dependencies import get_db
from .ledger import create_ledger_from_payment
from app.core.config import settings

# 환경 변수 및 키 설정
KAKAO_ADMIN_KEY = settings.KAKAO_ADMIN_KEY

# 라우터 설정
router = APIRouter(
    prefix="/payments",
    tags=["payments"],
    responses={404: {"description": "Not found"}},
)

# --- 카카오페이 CID 설정 ---
CID_ONETIME = "TC0ONETIME"       # 일반 결제 (이것만 사용)


# =========================================================
# 🛍️ [핵심] 일반 1회성 결제 (QR/PC)
# =========================================================

@router.post("/ready", response_model=schemas.PaymentReadyResponse)
async def payment_ready(
    request: schemas.PaymentReadyRequest,
    db: Session = Depends(get_db)
):
    """
    [결제 준비 API] 웹 키오스크에서 결제 QR 코드를 요청합니다.
    - 무게 검증 없이 즉시 결제를 준비합니다.
    """
    # 1. 세션 및 사용자 확인
    cart_session = db.query(models.CartSession).filter(
        models.CartSession.cart_session_id == request.cart_session_id
    ).first()
    
    if not cart_session:
        raise HTTPException(status_code=404, detail="해당 카트 세션을 찾을 수 없습니다.")

    user_id = cart_session.user_id
    if not user_id:
         raise HTTPException(status_code=400, detail="세션에 연결된 사용자가 없습니다.")

    # 2. 기존 미완료 결제 내역 정리
    existing_payment = db.query(models.Payment).filter(
        models.Payment.cart_session_id == request.cart_session_id,
        models.Payment.status == models.PaymentStatus.PENDING
    ).first()
    if existing_payment:
        db.delete(existing_payment)
        db.commit()

    # 3. 카카오페이 준비 API 호출
    url = "https://kapi.kakao.com/v1/payment/ready"
    headers = {
        "Authorization": f"KakaoAK {KAKAO_ADMIN_KEY}",
        "Content-type": "application/x-www-form-urlencoded;charset=utf-8"
    }
    
    # [수정] settings에서 직접 실시간 BASE_URL 가져오기
    base_url = settings.BASE_URL.rstrip('/')
    approval_url = f"{base_url}/api/payments/success?session_id={cart_session.cart_session_id}"
    cancel_url = f"{base_url}/api/payments/cancel?session_id={cart_session.cart_session_id}"
    fail_url = f"{base_url}/api/payments/fail?session_id={cart_session.cart_session_id}"

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
        logger.error(f"❌ 카카오페이 준비 실패: {res_data}")
        raise HTTPException(status_code=400, detail=f"KakaoPay Error: {res_data}")

    # 4. 결제 내역 저장 (PENDING 상태)
    new_payment = models.Payment(
        cart_session_id=cart_session.cart_session_id,
        user_id=user_id,
        pg_provider=models.PgProviderType.KAKAO_PAY,
        pg_tid=res_data['tid'],
        status=models.PaymentStatus.PENDING,
        total_amount=request.total_amount
    )
    db.add(new_payment)
    db.commit()

    return schemas.PaymentReadyResponse(
        tid=res_data['tid'],
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
    logger.info(f"🏁 콜백 수신 - Session ID: {session_id}")

    # 1. 대기 중인 결제 정보 조회
    payment = db.query(models.Payment).filter(
        models.Payment.cart_session_id == session_id,
        models.Payment.status == models.PaymentStatus.PENDING
    ).order_by(models.Payment.payment_id.desc()).first()

    if not payment:
        logger.error(f"❌ 결제 정보를 찾을 수 없음 - Session ID: {session_id}")
        return HTMLResponse(content="<h1>결제 정보를 찾을 수 없습니다.</h1>", status_code=404)

    # 2. 카카오페이 승인 API 호출
    url = "https://kapi.kakao.com/v1/payment/approve"
    headers = {
        "Authorization": f"KakaoAK {KAKAO_ADMIN_KEY}",
        "Content-type": "application/x-www-form-urlencoded;charset=utf-8"
    }
    
    # Ready 시점과 정확히 일치하는 파라미터 구성
    approve_data = {
        "cid": CID_ONETIME,
        "tid": payment.pg_tid,
        "partner_order_id": str(payment.cart_session_id),
        "partner_user_id": str(payment.user_id),
        "pg_token": pg_token
    }

    logger.info(f"--- 카카오 승인 요청 (TID: {payment.pg_tid}) ---")

    async with httpx.AsyncClient() as client:
        res = await client.post(url, headers=headers, data=approve_data)
        res_data = res.json()

    logger.info(f"--- 카카오 승인 응답: {res_data} ---")

    if "aid" in res_data:
        # 3. 승인 성공 시 상태 업데이트 및 세션 종료
        payment.status = models.PaymentStatus.APPROVED
        payment.approved_at = datetime.now()
        
        # 장바구니 세션 종료 처리
        db.query(models.CartSession).filter(
            models.CartSession.cart_session_id == session_id
        ).update({
            "status": models.CartSessionStatus.PAID,
            "ended_at": datetime.now()
        })

        db.commit()
        logger.info(f"✅ 결제 승인 성공 (Session: {session_id})")
        
        # 가계부 자동 등록
        try:
            create_ledger_from_payment(payment_id=payment.payment_id, db=db)
        except: pass

        return HTMLResponse(content="""
            <!DOCTYPE html>
            <html>
            <head>
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <style>
                    body { display:flex; flex-direction:column; align-items:center; justify-content:center; height:100vh; margin:0; font-family: sans-serif; background-color:#f8fafc; }
                    .card { background:white; padding:40px; border-radius:32px; box-shadow:0 20px 25px -5px rgba(0,0,0,0.1); text-align:center; max-width: 80%; }
                    h2 { color:#1e293b; margin:16px 0 8px 0; }
                    p { color:#64748b; margin:0; line-height:1.5; }
                    .btn { margin-top:24px; padding:12px 24px; background:#8b5cf6; color:white; border-radius:12px; text-decoration:none; font-weight:bold; display:inline-block; border:none; cursor:pointer; }
                </style>
            </head>
            <body>
                <div class="card">
                    <div style="font-size:64px;">✅</div>
                    <h2>결제 완료</h2>
                    <p>카카오톡 결제 알림을 확인해주세요.</p>
                    <p style="font-size:14px; color:#94a3b8; margin-top:10px;">이 창은 잠시 후 자동으로 닫힙니다.</p>
                    <button class="btn" onclick="window.close()">창 닫기</button>
                </div>
                <script>setTimeout(() => { window.close(); }, 3000);</script>
            </body>
            </html>
        """)
    
    # 실패 시 상세 에러 노출
    kakao_error = res_data.get('msg', '승인 처리 중 오류 발생')
    kakao_code = res_data.get('code', 'Unknown')
    logger.error(f"❌ 카카오 승인 실패: {kakao_error} (Code: {kakao_code})")
    
    return HTMLResponse(content=f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <style>
                body { display:flex; flex-direction:column; align-items:center; justify-content:center; height:100vh; margin:0; font-family: sans-serif; background-color:#fff1f2; }
                .card { background:white; padding:40px; border-radius:32px; box-shadow:0 20px 25px -5px rgba(0,0,0,0.1); text-align:center; max-width: 80%; }
                h2 { color:#991b1b; margin:16px 0 8px 0; }
                p { color:#7f1d1d; margin:0; }
                .btn { margin-top:24px; padding:12px 24px; background:#ef4444; color:white; border-radius:12px; text-decoration:none; font-weight:bold; display:inline-block; border:none; cursor:pointer; }
            </style>
        </head>
        <body>
            <div class="card">
                <div style="font-size:64px;">❌</div>
                <h2>결제 실패</h2>
                <p>{kakao_error}</p>
                <p style="font-size:12px; color:#94a3b8; margin-top:10px;">에러 코드: {kakao_code}</p>
                <button class="btn" onclick="window.close()">창 닫기</button>
            </div>
        </body>
        </html>
    """, status_code=400)


@router.get("/cancel")
async def payment_cancel_callback(session_id: int = None):
    return JSONResponse(content={"message": "결제가 취소되었습니다.", "session_id": session_id, "status": "CANCELLED"})


@router.get("/fail")
async def payment_fail_callback(session_id: int = None):
    return JSONResponse(content={"message": "결제에 실패하였습니다.", "session_id": session_id, "status": "FAILED"}, status_code=400)


# =========================================================
# 🔍 조회 및 기타 (필요시 사용)
# =========================================================

@router.get("/{payment_id}", response_model=schemas.PaymentDetailResponse)
async def get_payment_detail(
    payment_id: int,
    db: Session = Depends(get_db)
):
    """결제 상세 정보 조회"""
    payment = db.query(models.Payment).filter(models.Payment.payment_id == payment_id).first()
    if not payment:
        raise HTTPException(status_code=404, detail="결제 내역을 찾을 수 없습니다.")
    return payment
