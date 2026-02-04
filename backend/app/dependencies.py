import logging
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import AppUser
from app.utils.jwt import decode_token

# 로깅 설정
logger = logging.getLogger(__name__)

security = HTTPBearer()

def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
) -> AppUser:
    token = credentials.credentials  
    logger.info("--- 인증 시작: 토큰 수신 ---")

    try:
        payload = decode_token(token)
    except HTTPException as e:
        logger.error(f"❌ 인증 실패: 토큰 검증 에러 - {e.detail}")
        raise e
    except Exception as e:
        logger.error(f"❌ 인증 실패: 알 수 없는 토큰 에러 - {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
        )

    if payload is None:
        logger.error("❌ 인증 실패: 토큰 페이로드가 비어있음")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
        )

    user_id = payload.get("sub")
    if user_id is None:
        logger.error(f"❌ 인증 실패: 페이로드에 'sub' 필드가 없음: {payload}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token: sub missing",
        )

    logger.info(f"--- 인증 진행: 토큰에서 유저 ID {user_id} 확인 ---")

    try:
        user = db.get(AppUser, int(user_id))
    except Exception as e:
        logger.error(f"❌ 인증 실패: 유저 조회 중 DB 에러 발생: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database error during authentication",
        )

    if not user:
        logger.error(f"❌ 인증 실패: DB에서 유저 ID {user_id}를 찾을 수 없음")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    # DB에 is_active 컬럼이 없을 경우를 대비해 안전하게 확인
    is_active = getattr(user, 'is_active', True)
    if not is_active:
        logger.error(f"❌ 인증 실패: 비활성화된 유저 {user_id} ({user.email})")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Inactive user",
        )

    logger.info(f"✅ 인증 성공: 유저 {user.email} (ID: {user_id})")
    return user

