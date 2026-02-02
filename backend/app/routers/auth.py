# app/routers/auth.py
from fastapi import APIRouter, Cookie, HTTPException, Depends, status
from app.utils.jwt import decode_token, create_access_token, create_refresh_token
from sqlalchemy.orm import Session

from app.schemas import UserPasswordResetRequest, UserPasswordReset
from app.database import get_db
from app.models import AppUser, PasswordResetToken, UserProvider
from app.utils.security import hash_password

import uuid
from datetime import datetime, timedelta
from app.utils.email import send_reset_password_email
from os import getenv

import requests
from app import models, schemas
from app.core.config import settings   # settings에서 env 읽는 구조일 때

from fastapi import Query
from fastapi.responses import JSONResponse, RedirectResponse

router = APIRouter(prefix="/auth", tags=["auth"])


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


# TODO: SMTP blocked in SSAFY network
# TODO: Replace with SendGrid (HTTP API)

# 비밀번호 재설정 요청 API
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
    send_reset_password_email(user.email, reset_link)

    return {"message": "비밀번호 재설정 이메일을 전송했습니다."}


# 비밀번호 재설정 실행 API
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


# 구글 로그인
@router.post(
    "/google",
    response_model=schemas.TokenResponse,
)
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
        raise HTTPException(
            status_code=400,
            detail="Google token exchange failed",
        )

    google_access_token = token_res.json().get("access_token")

    # 2. 사용자 정보 조회
    user_res = requests.get(
        "https://www.googleapis.com/oauth2/v2/userinfo",
        headers={
            "Authorization": f"Bearer {google_access_token}"
        },
    )

    user_info = user_res.json()

    email = user_info.get("email")
    nickname = user_info.get("name")

    if not email:
        raise HTTPException(
            status_code=400,
            detail="Google user info invalid",
        )

    # 3. 사용자 조회
    user = (
        db.query(models.AppUser)
        .filter(
            models.AppUser.email == email,
            models.AppUser.provider == "GOOGLE",
        )
        .first()
    )

    # 4. 없으면 회원가입
    if not user:
        user = models.AppUser(
            email=email,
            nickname=nickname,
            provider="GOOGLE",
            password_hash=None,
        )
        db.add(user)
        db.commit()
        db.refresh(user)

    # 5. JWT 발급
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
    """
    Google OAuth redirect endpoint (프론트 미구현용)
    """
    # 기존 POST /auth/google 로직을 그대로 재사용
    oauth_request = schemas.GoogleOAuthRequest(code=code)
    return google_login(oauth_request, db)


# 카카오 로그인
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
def kakao_callback(
    code: str,
    db: Session = Depends(get_db),
):
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
        print("Kakao token error:", token_res.text)
        raise HTTPException(status_code=400, detail=token_res.text)

    access_token = token_res.json()["access_token"]

    # 2. 사용자 정보
    user_res = requests.get(
        "https://kapi.kakao.com/v2/user/me",
        headers={"Authorization": f"Bearer {access_token}"},
    )

    kakao_user = user_res.json()

    kakao_id = kakao_user["id"]
    nickname = kakao_user["properties"]["nickname"]

    email = None
    if "kakao_account" in kakao_user:
        email = kakao_user["kakao_account"].get("email")

    # 3. DB 조회
    user = (
        db.query(AppUser)
        .filter(
            AppUser.provider == UserProvider.KAKAO,
            AppUser.email == (email or f"kakao_{kakao_id}@kakao.com"),
        )
        .first()
    )

    # 4. 없으면 회원가입
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

    # 5. JWT 발급
    access_token = create_access_token(str(user.user_id))
    refresh_token = create_refresh_token(str(user.user_id))

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
    }

