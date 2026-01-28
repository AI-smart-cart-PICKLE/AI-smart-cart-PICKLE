# app/routers/auth.py
from fastapi import APIRouter, Cookie, HTTPException, Depends, status
from app.utils.jwt import decode_token, create_access_token
from sqlalchemy.orm import Session

from app.schemas import UserPasswordResetRequest, UserPasswordReset
from app.database import get_db
from app.models import AppUser, PasswordResetToken
from app.utils.security import hash_password

import uuid
from datetime import datetime, timedelta
from app.utils.email import send_reset_password_email
from os import getenv

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
