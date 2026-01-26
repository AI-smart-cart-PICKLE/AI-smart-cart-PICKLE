# app/routers/user.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.database import get_db
from app import schemas
from app.models import AppUser, UserProvider
from app.utils.security import hash_password, verify_password
from app.utils.jwt import create_access_token, create_refresh_token
from app.dependencies import get_current_user

router = APIRouter(prefix="/api", tags=["User"])


# 회원가입
@router.post("/auth/signup", response_model=schemas.UserResponse)
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
@router.post("/auth/login", response_model=schemas.TokenResponse)
def login(
    request: schemas.UserLogin,
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

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer"
    }


# 내 정보 조회
@router.get("/users/me", response_model=schemas.UserResponse)
def read_me(
    current_user: AppUser = Depends(get_current_user)
):
    return current_user
