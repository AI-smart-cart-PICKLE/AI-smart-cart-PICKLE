from pydantic import BaseModel, Field, EmailStr, field_validator, ConfigDict
from typing import Optional
from datetime import datetime, date
from .models import PaymentMethodType, PgProviderType, PaymentStatus, LedgerCategory, DetectionActionType, UserProvider
import re

# --- Payment Method Schemas ---

class PaymentMethodBase(BaseModel):
    method_type: PaymentMethodType
    billing_key: Optional[str] = None
    card_brand: Optional[str] = None
    card_last4: Optional[str] = Field(None, min_length=4, max_length=4)
    is_default: bool = False

class PaymentMethodCreate(PaymentMethodBase):
    pass

class PaymentMethodResponse(PaymentMethodBase):
    method_id: int
    user_id: int
    created_at: datetime

    class Config:
        from_attributes = True

# --- Payment Schemas ---

class PaymentReadyRequest(BaseModel):
    cart_session_id: int
    # 0보다 커야 한다는 제약조건 추가 (해킹 방지)
    total_amount: int = Field(..., gt=0, description="결제 금액은 0원 이상이어야 합니다.") 
    method_id: Optional[int] = None

class PaymentReadyResponse(BaseModel):
    tid: str
    next_redirect_app_url: Optional[str] = None
    next_redirect_mobile_url: Optional[str] = None
    next_redirect_pc_url: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.now)

class PaymentApproveRequest(BaseModel):
    tid: str
    pg_token: str
    partner_order_id: str  # cart_session_id (문자열 변환)
    partner_user_id: str   # user_id (문자열 변환)

class PaymentResponse(BaseModel):
    payment_id: int
    cart_session_id: Optional[int]
    user_id: int
    method_id: Optional[int]
    pg_provider: PgProviderType
    pg_tid: Optional[str]
    status: PaymentStatus
    total_amount: int
    approved_at: Optional[datetime]

    class Config:
        from_attributes = True
        
# 결제 취소 요청
class PaymentCancelRequest(BaseModel):
    reason: str = "사용자 요청에 의한 취소"

# 결제 상세 조회 응답 (기존 PaymentResponse 활용 가능하지만, 명확히 하려면 분리)
class PaymentDetailResponse(PaymentResponse):
    pass

# --- Ledger Schemas (가계부 연동을 위해 미리 정의) ---

class LedgerEntryResponse(BaseModel):
    ledger_entry_id: int
    user_id: int
    payment_id: Optional[int]
    spend_date: date
    category: LedgerCategory
    amount: int

    class Config:
        from_attributes = True


# --- user schemas ---

NICKNAME_REGEX = re.compile(r"^[A-Za-z가-힣]{2,20}$")

class UserBase(BaseModel):
    email: EmailStr
    nickname: str = Field(min_length=2, max_length=8)


class UserCreate(BaseModel):
    email: EmailStr
    password: str
    nickname: str

    # 비밀번호 검증
    @field_validator("password")
    @classmethod
    def validate_password(cls, value: str) -> str:
        """
        비밀번호 정책:
        - 최소 8자
        - 영문 + 숫자 조합
        """
        if len(value) < 8:
            raise ValueError("Password must be at least 8 characters long")

        if not re.search(r"[A-Za-z]", value) or not re.search(r"\d", value):
            raise ValueError("Password must contain both letters and numbers")

        return value

    # 닉네임 검증
    @field_validator("nickname")
    @classmethod
    def validate_nickname(cls, value: str) -> str:
        """
        닉네임 정책:
        - 한글 또는 영어만 허용
        - 최소 2자, 최대 20자
        - 중복 허용 (DB에서 UNIQUE 제약 없음)
        """
        if not NICKNAME_REGEX.fullmatch(value):
            raise ValueError(
                "Nickname must be 2–20 characters long and contain only Korean or English letters"
            )
        return value


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    user_id: int
    email: EmailStr
    provider: UserProvider
    nickname: str
    created_at: datetime
    updated_at: Optional[datetime]



class UserUpdate(BaseModel):
    nickname: str = Field(min_length=2, max_length=8)


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: Optional[str] = None
    token_type: str = "bearer"


class EmailCheckResponse(BaseModel):
    is_available: bool
