# app/routers/auth.py
from fastapi import APIRouter, Cookie, HTTPException, Depends, status, Query
from fastapi.responses import JSONResponse, RedirectResponse
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
import uuid
import requests
from os import getenv

# 내부 모듈 임포트
from app import models, schemas
from app.database import get_db
from app.models import (
    AppUser, PasswordResetToken, UserProvider, 
    CartDevice, CartSession, CartSessionStatus
)
from app.schemas import UserPasswordResetRequest, UserPasswordReset
from app.utils.jwt import decode_token, create_access_token, create_refresh_token
from app.utils.security import hash_password
from app.utils.email import send_reset_password_email
from app.core.config import settings
from app.core.redis_client import get_redis
from app.dependencies import get_current_user # 유저 정보 추출용

router = APIRouter(prefix="/auth", tags=["auth"])


# =========================================================
# 🔄 토큰 관리 (Refresh)
# =========================================================

@router.post("/refresh")
def refresh_access_token(refresh_token: str = Cookie(None)):
    if not refresh_token:
        raise HTTPException(status_code=401, detail="Refresh token missing")

    payload = decode_token(refresh_token)

    if payload.get("type") != "refresh":
        raise HTTPException(status_code=401, detail="Invalid token type")

    new_access_token = create_access_token(payload["sub"])

    return {
        "access_token": new_access_token,
        "token_type": "bearer",
    }


# =========================================================
# 🔒 비밀번호 재설정 (Reset Password)
# =========================================================

@router.post("/password/reset-request")
def request_password_reset(
    request: UserPasswordResetRequest,
    db: Session = Depends(get_db)
):
    user = db.query(AppUser).filter(AppUser.email == request.email).first()

    if not user:
        raise HTTPException(
            status_code=404,
            detail="해당 이메일로 가입된 회원이 없습니다."
        )

    reset_token = str(uuid.uuid4())
    expires_at = datetime.utcnow() + timedelta(minutes=30)

    token_row = PasswordResetToken(
        token=reset_token,
        user_id=user.user_id,
        expires_at=expires_at,
        used=False
    )

    db.add(token_row)
    db.commit()

    reset_link = f"{getenv('FRONTEND_URL')}/reset-password?token={reset_token}"
    # send_reset_password_email(user.email, reset_link) # SMTP 설정 필요 시 주석 해제

    return {"message": "비밀번호 재설정 이메일을 전송했습니다."}


@router.post("/password/reset")
def reset_password(
    request: UserPasswordReset,
    db: Session = Depends(get_db)
):
    token_row = (
        db.query(PasswordResetToken)
        .filter(PasswordResetToken.token == request.token)
        .first()
    )

    if not token_row:
        raise HTTPException(status_code=400, detail="유효하지 않은 토큰입니다.")

    if token_row.used:
        raise HTTPException(status_code=400, detail="이미 사용된 토큰입니다.")

    if token_row.expires_at < datetime.utcnow():
        raise HTTPException(status_code=400, detail="토큰이 만료되었습니다.")

    user = (
        db.query(AppUser)
        .filter(AppUser.user_id == token_row.user_id)
        .first()
    )

    user.password_hash = hash_password(request.new_password)
    token_row.used = True

    db.commit()

    return {"message": "비밀번호가 성공적으로 변경되었습니다."}


# =========================================================
# 🌍 소셜 로그인 (Google / Kakao)
# =========================================================

@router.post("/google", response_model=schemas.TokenResponse)
def google_login(
    request: schemas.GoogleOAuthRequest,
    db: Session = Depends(get_db),
):
    # 1. code → access token
    token_res = requests.post(
        "https://oauth2.googleapis.com/token",
        data={
            "client_id": settings.GOOGLE_CLIENT_ID,
            "client_secret": settings.GOOGLE_CLIENT_SECRET,
            "code": request.code,
            "grant_type": "authorization_code",
            "redirect_uri": settings.GOOGLE_REDIRECT_URI,
        },
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )

    if token_res.status_code != 200:
        raise HTTPException(status_code=400, detail="Google token exchange failed")

    google_access_token = token_res.json().get("access_token")

    # 2. 사용자 정보 조회
    user_res = requests.get(
        "https://www.googleapis.com/oauth2/v2/userinfo",
        headers={"Authorization": f"Bearer {google_access_token}"},
    )

    user_info = user_res.json()
    email = user_info.get("email")
    nickname = user_info.get("name")

    if not email:
        raise HTTPException(status_code=400, detail="Google user info invalid")

    # 3. 사용자 조회 및 가입
    user = db.query(models.AppUser).filter(
        models.AppUser.email == email,
        models.AppUser.provider == UserProvider.GOOGLE,
    ).first()

    if not user:
        user = models.AppUser(
            email=email,
            nickname=nickname,
            provider=UserProvider.GOOGLE,
            password_hash=None,
        )
        db.add(user)
        db.commit()
        db.refresh(user)

    # 4. JWT 발급
    access_token = create_access_token(str(user.user_id))
    refresh_token = create_refresh_token(str(user.user_id))

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
    }


@router.get("/google/callback")
def google_callback(
    code: str = Query(...),
    db: Session = Depends(get_db),
):
    oauth_request = schemas.GoogleOAuthRequest(code=code)
    return google_login(oauth_request, db)


@router.get("/kakao/login")
def kakao_login():
    kakao_auth_url = (
        "https://kauth.kakao.com/oauth/authorize"
        f"?client_id={settings.KAKAO_REST_API_KEY}"
        f"&redirect_uri={settings.KAKAO_REDIRECT_URI}"
        "&response_type=code"
    )
    return RedirectResponse(kakao_auth_url)


@router.get("/kakao/callback")
def kakao_callback(code: str, db: Session = Depends(get_db)):
    # 1. 토큰 요청
    token_res = requests.post(
        "https://kauth.kakao.com/oauth/token",
        data={
            "grant_type": "authorization_code",
            "client_id": settings.KAKAO_REST_API_KEY,
            "redirect_uri": settings.KAKAO_REDIRECT_URI,
            "code": code,
        },
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )

    if token_res.status_code != 200:
        raise HTTPException(status_code=400, detail="Kakao token exchange failed")

    access_token = token_res.json()["access_token"]

    # 2. 사용자 정보
    user_res = requests.get(
        "https://kapi.kakao.com/v2/user/me",
        headers={"Authorization": f"Bearer {access_token}"},
    )

    kakao_user = user_res.json()
    kakao_id = kakao_user["id"]
    nickname = kakao_user["properties"]["nickname"]
    email = kakao_user.get("kakao_account", {}).get("email")

    # 3. DB 조회 및 가입
    user = db.query(AppUser).filter(
        AppUser.provider == UserProvider.KAKAO,
        AppUser.email == (email or f"kakao_{kakao_id}@kakao.com"),
    ).first()

    if not user:
        user = AppUser(
            email=email or f"kakao_{kakao_id}@kakao.com",
            nickname=nickname,
            provider=UserProvider.KAKAO,
            password_hash=None,
        )
        db.add(user)
        db.commit()
        db.refresh(user)

    # 4. JWT 발급
    access_token = create_access_token(str(user.user_id))
    refresh_token = create_refresh_token(str(user.user_id))

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
    }


# =========================================================
# 📱 IoT 디바이스 로그인 (Static QR + Redis Handshake)
# [NEW] 포트폴리오 핵심 기능: Redis를 활용한 O2O 인증 및 Polling 최적화
# =========================================================

# 1. [앱] QR 스캔 (사용자가 카트를 '찜'하는 API)
@router.post("/device/connect", summary="[앱] 카트 QR 스캔 및 사용자 매핑")
def connect_device(
    device_code: str,   # QR에서 읽은 고정 값 (예: "CART_A202_01")
    current_user: models.AppUser = Depends(get_current_user), # 토큰에서 유저 정보 추출
    redis=Depends(get_redis),
    db: Session = Depends(get_db)
):
    """
    [앱] 사용자가 카트에 붙은 고정 QR(device_code)을 찍으면 호출됩니다.
    - Redis에 '이 디바이스는 이 유저가 쓸 거야'라고 임시 저장합니다. (TTL 60초)
    - 이를 통해 DB 부하 없이 빠른 핸드쉐이크를 준비합니다.
    """
    # 1. 유효한 디바이스인지 DB 확인
    device = db.query(CartDevice).filter(CartDevice.device_code == device_code).first()
    if not device:
        raise HTTPException(status_code=404, detail="등록되지 않은 카트 디바이스입니다.")

    # 2. Redis Key 설정
    redis_key = f"device_login:{device_code}"
    
    # 3. 이미 누군가 점유 중인지 체크 (Concurrency Control)
    if redis.exists(redis_key):
         raise HTTPException(status_code=409, detail="다른 사용자가 연결을 시도 중인 카트입니다.")

    # 4. 매핑 저장 (Key: device_code, Value: user_id, TTL: 60초)
    redis.setex(redis_key, 60, str(current_user.user_id))
    
    return {"message": f"카트({device_code})와 연결을 시도합니다."}


# 2. [카트] 로그인 상태 확인 (Polling)
@router.get("/device/poll/{device_code}", summary="[카트] 로그인 요청 확인 (Polling)")
def poll_device_login(
    device_code: str,
    redis=Depends(get_redis),
    db: Session = Depends(get_db)
):
    """
    [카트] 태블릿이 1~2초마다 호출하여 자신이 매핑되었는지 확인합니다.
    - Redis 조회만 수행하므로 DB 부하가 '0'에 가깝습니다.
    - 매핑 정보 발견 시 -> 세션을 생성하고 로그인 완료 처리를 합니다.
    """
    redis_key = f"device_login:{device_code}"
    user_id_str = redis.get(redis_key)
    
    # 1. 아직 아무도 안 찍었음 (Waiting)
    if not user_id_str:
        return {"status": "WAITING"}
    
    # 2. 누군가 찍었음! (로그인 진행)
    user_id = int(user_id_str)
    
    # --- 여기서부터는 '로그인 확정' 트랜잭션 ---
    
    # 디바이스 정보 조회
    device = db.query(CartDevice).filter(CartDevice.device_code == device_code).first()
    if not device:
        return {"status": "ERROR", "message": "Device not found in DB"}

    # 기존에 열려있는 세션이 있다면 종료 처리 (Clean up)
    active_session = db.query(CartSession).filter(
        CartSession.cart_device_id == device.cart_device_id,
        CartSession.status == CartSessionStatus.ACTIVE
    ).first()
    
    if active_session:
        active_session.status = CartSessionStatus.CANCELLED
        active_session.ended_at = datetime.now()
    
    # 새 세션 생성 (DB 저장)
    new_session = CartSession(
        cart_device_id=device.cart_device_id,
        user_id=user_id,
        status=CartSessionStatus.ACTIVE,
        started_at=datetime.now()
    )
    db.add(new_session)
    db.commit()
    db.refresh(new_session)
    
    # Redis 키 삭제 (재사용 방지 & 보안)
    redis.delete(redis_key)
    
    # 유저 닉네임 가져오기 (환영 메시지용)
    user = db.query(models.AppUser).filter(models.AppUser.user_id == user_id).first()
    
    return {
        "status": "COMPLETED",
        "cart_session_id": new_session.cart_session_id,
        "user_nickname": user.nickname,
        "message": "로그인되었습니다!"
    }