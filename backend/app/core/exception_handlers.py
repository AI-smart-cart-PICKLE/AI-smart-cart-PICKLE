# app/core/exception_handlers.py
from fastapi import Request, HTTPException, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
import logging
import traceback

# 로거 설정
logger = logging.getLogger("app.core.exceptions")

# 1. 예상치 못한 서버 에러 (500) 처리
async def global_exception_handler(request: Request, exc: Exception):
    """
    모든 처리되지 않은 예외(500 Internal Server Error)를 여기서 잡습니다.
    - 서버 로그에는 상세한 스택 트레이스(Stack Trace)를 남깁니다. (디버깅용)
    - 클라이언트에게는 '시스템 에러가 발생했습니다'라는 안전한 메시지만 보냅니다. (보안용)
    """
    # 에러 로그 상세 기록 (파일이나 콘솔에 찍힘)
    error_msg = f"❌ [Global Exception] {str(exc)}\nURL: {request.url}\n{traceback.format_exc()}"
    logger.error(error_msg)

    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "status": "error",
            "code": "INTERNAL_SERVER_ERROR",
            "message": "서버 내부 오류가 발생했습니다. 잠시 후 다시 시도해주세요.",
            "path": str(request.url)
        },
    )

# 2. HTTP 에러 (400, 401, 404 등) 처리
async def http_exception_handler(request: Request, exc: HTTPException):
    """
    개발자가 의도적으로 발생시킨 HTTPException을 잡습니다.
    예: raise HTTPException(status_code=404, detail="상품 없음")
    """
    logger.warning(f"⚠️ [HTTP Exception] {exc.detail} (Path: {request.url})")
    
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "status": "fail",
            "code": f"HTTP_{exc.status_code}",
            "message": exc.detail,
            "path": str(request.url)
        },
    )

# 3. 유효성 검사 실패 (Pydantic Validation Error) 처리
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """
    요청 데이터 형식이 틀렸을 때 (예: 이메일 필드에 한글 입력) 발생합니다.
    """
    logger.info(f"🔍 [Validation Error] {exc.errors()} (Path: {request.url})")
    
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "status": "fail",
            "code": "VALIDATION_ERROR",
            "message": "입력 값이 올바르지 않습니다.",
            "details": exc.errors(), # 어디가 틀렸는지 상세 정보 포함
            "path": str(request.url)
        },
    )