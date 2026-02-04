# app/routers/user.py
from fastapi import APIRouter, Depends, HTTPException, status, Response
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.database import get_db
from app import schemas
from app.models import AppUser, UserProvider
from app.utils.security import hash_password, verify_password
from app.utils.jwt import create_access_token, create_refresh_token
from app.dependencies import get_current_user
from app.schemas import UserNicknameUpdate, UserPasswordUpdate
from datetime import datetime


# Auth 관련 라우터 (회원가입, 로그인, 로그아웃)
auth_router = APIRouter(prefix="/auth", tags=["Auth"])

# User 관련 라우터 (내 정보, 프로필 관리)
user_router = APIRouter(prefix="/users", tags=["User"])


# 회원가입
@auth_router.post("/signup", response_model=schemas.UserMeResponse)
def signup(
    request: schemas.UserCreate,
    db: Session = Depends(get_db)
):
    try:
        user = AppUser(
            email=request.email,
            password_hash=hash_password(request.password),
            nickname=request.nickname,
            provider=UserProvider.LOCAL
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        return user

    # 이메일 중복
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )

    # 해시 과정에서 발생하는 예외를 422로 변환 (서버 500 방지)
    except ValueError as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(e)
        )

# 로그인
@auth_router.post("/login")
def login(
    request: schemas.UserLogin,
    response: Response,             
    db: Session = Depends(get_db)
):
    user = (
        db.query(AppUser)
        .filter(AppUser.email == request.email)
        .first()
    )

    if not user or not user.password_hash:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )

    if not verify_password(request.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )

    access_token = create_access_token(str(user.user_id))
    refresh_token = create_refresh_token(str(user.user_id))

    # Refresh Token을 HttpOnly Cookie로 설정
    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        samesite="lax",
        secure=False,   # HTTPS면 True
        path="/"
    )

    # dict로 반환 (FastAPI가 JSON Response 자동 생성)
    return {
        "access_token": access_token,
        "token_type": "bearer"
    }

# 로그아웃
@auth_router.post("/logout")
def logout(
    response: Response,
    db: Session = Depends(get_db),
    current_user: AppUser = Depends(get_current_user)
):
    # 1. 사용자의 모든 활성 카트 세션 종료
    db.query(AppUser).filter(AppUser.user_id == current_user.user_id).update({"updated_at": datetime.now()}) # dummy update to ensure session
    from app.models import CartSession, CartSessionStatus
    db.query(CartSession).filter(
        CartSession.user_id == current_user.user_id,
        CartSession.status == CartSessionStatus.ACTIVE
    ).update({"status": CartSessionStatus.CANCELLED, "ended_at": datetime.now()})
    
    db.commit()

    # 2. 쿠키 삭제
    response.delete_cookie(
        key="refresh_token",
        path="/",
    )
    return {"message": "Logged out successfully and cart sessions closed"}


# 내 정보 조회
@user_router.get("/me", response_model=schemas.UserMeResponse)
def read_me(
    current_user: AppUser = Depends(get_current_user)
):
    return current_user

# 닉네임 변경
@user_router.patch("/me/nickname", response_model=schemas.UserMeResponse)
def update_nickname(
    req: schemas.UserNicknameUpdate,
    db: Session = Depends(get_db),
    current_user: AppUser = Depends(get_current_user),
):
    current_user.nickname = req.nickname
    db.commit()
    db.refresh(current_user)
    return current_user


# 비밀번호 변경
@user_router.patch("/me/password")
def update_password(
    req: schemas.UserPasswordUpdate,
    db: Session = Depends(get_db),
    current_user: AppUser = Depends(get_current_user),
):
    # OAuth 유저 차단
    if current_user.provider != UserProvider.LOCAL:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="OAuth users cannot change password"
        )

    # 현재 비밀번호 검증 
    if not verify_password(req.current_password, current_user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Current password is incorrect"
        )

    current_user.password_hash = hash_password(req.new_password)
    db.commit()

    return {"message": "Password updated successfully"}


# 회원탈퇴
@user_router.delete("/me")
def withdraw_user(
    req: schemas.UserWithdraw,
    response: Response,
    db: Session = Depends(get_db),
    current_user: AppUser = Depends(get_current_user),
):
    # 이미 탈퇴한 유저 방어
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User already withdrawn"
        )

    # LOCAL 유저 → 비밀번호 검증
    if current_user.provider == UserProvider.LOCAL:
        if not req.password:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Password is required"
            )
        if not verify_password(req.password, current_user.password_hash):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Password is incorrect"
            )

    # Soft delete 처리
    current_user.is_active = False
    current_user.deleted_at = datetime.utcnow()
    db.commit()

    # 로그아웃 처리 (refresh token 제거)
    response.delete_cookie(
        key="refresh_token",
        path="/"
    )

    return {"message": "Account withdrawn successfully"}
