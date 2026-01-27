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


router = APIRouter(prefix="/api", tags=["User"])


# 회원가입
@router.post("/auth/signup", response_model=schemas.UserMeResponse)
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
@router.post("/auth/login")
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
@router.post("/auth/logout")
def logout(response: Response):
    response.delete_cookie(
        key="refresh_token",
        path="/",
    )
    return {"message": "Logged out successfully"}


# 내 정보 조회
@router.get("/users/me", response_model=schemas.UserMeResponse)
def read_me(
    current_user: AppUser = Depends(get_current_user)
):
    return current_user

# 닉네임 변경
@router.patch("/users/me/nickname", response_model=schemas.UserMeResponse)
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
@router.patch("/users/me/password")
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