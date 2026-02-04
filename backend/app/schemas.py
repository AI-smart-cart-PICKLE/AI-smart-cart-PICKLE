from pydantic import BaseModel, Field, EmailStr, field_validator, ConfigDict
from typing import Optional, List, Dict, Any
from datetime import datetime, date
from .models import PaymentMethodType, PgProviderType, PaymentStatus, LedgerCategory, DetectionActionType, UserProvider
import re


# =========================================================
# 💳 Payment Method Schemas (결제 수단)
# =========================================================

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


# =========================================================
# 💰 Payment Schemas (결제)
# =========================================================

# 1. 결제 준비 (Ready)
class PaymentReadyRequest(BaseModel):
    cart_session_id: int
    total_amount: int = Field(..., gt=0, description="결제 금액은 0원 이상이어야 합니다.") 
    method_id: Optional[int] = None

    model_config = ConfigDict(json_schema_extra={
        "example": {
            "cart_session_id": 12,
            "total_amount": 15000,
            "method_id": None
        }
    })

class PaymentReadyResponse(BaseModel):
    tid: str
    next_redirect_app_url: Optional[str] = None
    next_redirect_mobile_url: Optional[str] = None
    next_redirect_pc_url: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.now)
    partner_order_id: Optional[str] = None

# 2. 결제 승인 (Approve)
class PaymentApproveRequest(BaseModel):
    tid: str
    pg_token: str
    partner_order_id: str
    partner_user_id: str

# 3. 결제 내역 응답
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

# 4. 결제 취소
class PaymentCancelRequest(BaseModel):
    reason: str = "사용자 요청에 의한 취소"

class PaymentDetailResponse(PaymentResponse):
    items: List["CartItemResponse"] = []

# --- ✨ [NEW] 결제 요청 및 무게 검증 (Checkout) ---

class PaymentRequest(BaseModel):
    """웹에서 결제하기 버튼 클릭 시 전송하는 데이터"""
    cart_session_id: int
    amount: int
    measured_weight_g: int = Field(..., description="Jetson/센서로부터 측정한 현재 무게")
    use_subscription: bool = True  # 기본적으로 자동결제 사용

    model_config = ConfigDict(json_schema_extra={
        "example": {
            "cart_session_id": 5,
            "amount": 25000,
            "measured_weight_g": 1500,
            "use_subscription": True
        }
    })

class PaymentWarningResponse(BaseModel):
    """무게 불일치 시 반환하는 경고 데이터 (409 Conflict)"""
    status: str = "WARNING"
    message: str
    difference: int
    expected_weight: int
    measured_weight: int
    action_required: str = "CHECK_CART_ITEMS"  # 프론트엔드 식별용


# =========================================================
# 🔑 Billing Key Schemas (카드 등록)
# =========================================================

class CardRegisterResponse(BaseModel):
    next_redirect_mobile_url: str
    next_redirect_pc_url: str
    tid: str
    created_at: datetime

class CardRegisterResult(BaseModel):
    method_id: int
    card_name: str
    billing_key: str
    message: str = "카드 등록이 완료되었습니다."


# =========================================================
# 📒 Ledger Schemas (가계부)
# =========================================================

class LedgerEntryResponse(BaseModel):
    ledger_entry_id: int
    user_id: int
    payment_id: Optional[int]
    spend_date: date
    category: LedgerCategory
    amount: int
    memo: Optional[str]

    class Config:
        from_attributes = True

class LedgerUpdateRequest(BaseModel):
    category: Optional[LedgerCategory] = None
    memo: Optional[str] = None

    model_config = ConfigDict(json_schema_extra={
        "example": {
            "category": "SNACK",
            "memo": "편의점 간식 구매"
        }
    })


# =========================================================
# 👤 User Schemas (회원)
# =========================================================

NICKNAME_REGEX = re.compile(r"^[A-Za-z가-힣0-9]{2,8}$")

class UserBase(BaseModel) :
    email: EmailStr
    nickname: str = Field(min_length=2, max_length=8)

class UserCreate(BaseModel):
    email: EmailStr
    password: str
    nickname: str

    @field_validator("password")
    @classmethod
    def validate_password(cls, value: str) -> str:
        if len(value) < 8:
            raise ValueError("Password must be at least 8 characters long")
        if not re.search(r"[A-Za-z]", value) or not re.search(r"\d", value):
            raise ValueError("Password must contain both letters and numbers")
        return value

    @field_validator("nickname")
    @classmethod
    def validate_nickname(cls, value: str) -> str:
        if not NICKNAME_REGEX.fullmatch(value):
            raise ValueError("Nickname must be 2–20 characters long and contain only Korean or English letters")
        return value

    model_config = ConfigDict(json_schema_extra={
        "example": {
            "email": "user@example.com",
            "password": "Password123!",
            "nickname": "행복한쇼핑"
        }
    })

class UserLogin(BaseModel):
    email: EmailStr
    password: str

    model_config = ConfigDict(json_schema_extra={
        "example": {
            "email": "user@example.com",
            "password": "Password123!"
        }
    })

class UserMeResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    user_id: int
    email: EmailStr
    provider: UserProvider
    nickname: str
    created_at: datetime
    updated_at: Optional[datetime]

class UserNicknameUpdate(BaseModel):
    nickname: str = Field(min_length=2, max_length=20)

class UserPasswordUpdate(BaseModel):
    current_password: str
    new_password: str

class UserPasswordResetRequest(BaseModel):
    email: EmailStr

class UserPasswordReset(BaseModel):
    token: str
    new_password: str = Field(min_length=8)

class TokenResponse(BaseModel):
    access_token: str
    refresh_token: Optional[str] = None
    token_type: str = "bearer"

class EmailCheckResponse(BaseModel):
    is_available: bool

class UserWithdraw(BaseModel):
    password: Optional[str] = None

class GoogleOAuthRequest(BaseModel):
    code: str


# =========================================================
# 🛒 Cart Schemas (장바구니)
# =========================================================

# 기기 기반 상품 동기화 (AI 추론 서버용)
class CartSyncItem(BaseModel):
    product_name: str
    quantity: int

class CartSyncRequest(BaseModel):
    device_code: str
    items: List[CartSyncItem]

class CartItemCreate(BaseModel):
    product_id: int
    quantity: int = Field(default=1, ge=1)

    model_config = ConfigDict(json_schema_extra={
        "example": {
            "product_id": 101,
            "quantity": 2
        }
    })

class ProductSimpleResponse(BaseModel):
    product_id: int
    name: str
    price: int
    image_url: Optional[str] = None
    
    class Config:
        from_attributes = True

class CartItemResponse(BaseModel):
    cart_item_id: int
    product: ProductSimpleResponse
    quantity: int
    unit_price: int
    total_price: int
    
    class Config:
        from_attributes = True

class CartSessionResponse(BaseModel):
    cart_session_id: int
    status: str
    total_amount: int
    total_items: int = 0
    expected_total_g: int = 0
    items: List[CartItemResponse] = Field(default_factory=list)
    
    class Config:
        from_attributes = True

class CartItemUpdate(BaseModel):
    quantity: int = Field(..., ge=1)

# --- Cart Weight Validation ---
class CartWeightValidateRequest(BaseModel):
    cart_session_id: int
    measured_weight_g: int = Field(..., gt=0)

    model_config = ConfigDict(json_schema_extra={
        "example": {
            "cart_session_id": 5,
            "measured_weight_g": 520
        }
    })

class CartWeightValidateResponse(BaseModel):
    is_valid: bool
    status: str  # MATCH | OVER_WEIGHT | UNDER_WEIGHT
    expected_weight: int
    measured_weight: int
    difference: int
    tolerance: int
    message: str


# =========================================================
# 🍳 Recipe & Product Schemas (추천 및 상품)
# =========================================================

class IngredientSimpleResponse(BaseModel):
    product_id: int
    name: str
    is_owned: bool
    
    class Config:
        from_attributes = True

class RecipeRecommendResponse(BaseModel):
    recipe_id: int
    title: str
    description: Optional[str] = None
    image_url: Optional[str] = None
    
    # AI 추천 점수
    similarity_score: Optional[float] = None
    
    # 전체 재료
    ingredients: List[IngredientSimpleResponse] = []

    # 부족한 재료
    missing_ingredients: List[IngredientSimpleResponse] = []
    
    class Config:
        from_attributes = True

class ProductResponse(BaseModel):
    product_id: int
    name: str
    price: int
    stock_quantity: Optional[int] = 0
    image_url: Optional[str] = None
    product_info: Optional[Dict[str, Any]] = None

    class Config:
        from_attributes = True

class RecipeIngredientResponse(BaseModel):
    product_id: int
    name: str
    quantity_info: Optional[str] = None
    image_url: Optional[str] = None

    class Config:
        from_attributes = True

class RecipeDetailResponse(BaseModel):
    recipe_id: int
    title: str
    description: Optional[str] = None
    instructions: Optional[str] = None
    image_url: Optional[str] = None

    # 조리 재료
    ingredients: List[RecipeIngredientResponse] = []

    class Config:
        from_attributes = True
