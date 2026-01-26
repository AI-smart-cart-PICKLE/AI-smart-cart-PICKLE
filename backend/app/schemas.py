from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime, date
from .models import PaymentMethodType, PgProviderType, PaymentStatus, LedgerCategory, DetectionActionType

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

# 결제 취소 요청
class PaymentCancelRequest(BaseModel):
    reason: str = "사용자 요청에 의한 취소"

# 결제 상세 조회 응답 (기존 PaymentResponse 활용 가능하지만, 명확히 하려면 분리)
class PaymentDetailResponse(PaymentResponse):
    pass