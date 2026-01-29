from pydantic import BaseModel, Field, EmailStr, field_validator, ConfigDict
from typing import Optional, List
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

# 결제 상세 조회 응답
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
    memo: Optional[str]

    class Config:
        from_attributes = True

class LedgerUpdateRequest(BaseModel):
    category: Optional[LedgerCategory] = None
    memo: Optional[str] = None


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

# 구글 로그인
class GoogleOAuthRequest(BaseModel):
    code: str


# --- Cart Schemas ---

# 1. 상품 담기 요청
class CartItemCreate(BaseModel):
    product_id: int
    quantity: int = Field(default=1, ge=1) # 1개 이상 필수

# 2. 상품 간단 정보 (CartItemResponse 내부용)
class ProductSimpleResponse(BaseModel):
    product_id: int
    name: str
    price: int
    image_url: Optional[str] = None
    
    class Config:
        from_attributes = True

# 3. 장바구니 아이템 응답
class CartItemResponse(BaseModel):
    cart_item_id: int
    product: ProductSimpleResponse  # 상품 정보 중첩
    quantity: int
    unit_price: int
    total_price: int  # @property 대신 일반 필드로 변경 (확실한 직렬화 위해)
    
    class Config:
        from_attributes = True

# 4. 장바구니 세션 응답 (최종 응답)
class CartSessionResponse(BaseModel):
    cart_session_id: int
    status: str
    total_amount: int
    total_items: int = 0      # 상품 종수(또는 개수)
    expected_total_g: int = 0 # 예상 무게 (기본값 추가)
    
    # 장바구니 아이템 목록
    items: List[CartItemResponse] = Field(default_factory=list)
    
    class Config:
        from_attributes = True

# 상품 수량 변경
class CartItemUpdate(BaseModel):
    quantity: int = Field(..., ge=1)


# --- Cart Weight Validation ---

class CartWeightValidateRequest(BaseModel):
    cart_session_id: int
    measured_weight_g: int = Field(..., gt=0)

class CartWeightValidateResponse(BaseModel):
    is_valid: bool
    status: str  # MATCH | OVER_WEIGHT | UNDER_WEIGHT
    expected_weight: int
    measured_weight: int
    difference: int
    tolerance: int
    message: str


# --- 레시피 추천 Schemas ---

class IngredientSimpleResponse(BaseModel):
    product_id: int
    name: str
    is_owned: bool  # 장바구니에 이미 있나?
    
    class Config:
        from_attributes = True

class RecipeRecommendResponse(BaseModel):
    recipe_id: int
    title: str
    description: Optional[str] = None
    image_url: Optional[str] = None
    difficulty: str = "NORMAL" # DB에 컬럼이 없다면 기본값 or models.py 확인 필요 (현재 models.py엔 없음, 필요시 추가)
    cooking_time_min: int = 30 # 상동
    
    # AI 추천 점수 (거리 기반: 0에 가까울수록 유사함)
    similarity_score: Optional[float] = None
    
    # 재료 분석
    missing_ingredients: List[IngredientSimpleResponse] = []
    
    class Config:
        from_attributes = True

# --- Product Schemas ---

class ProductResponse(BaseModel):
    product_id: int
    name: str
    price: int
    stock_quantity: Optional[int] = 0
    image_url: Optional[str] = None
    product_info: Optional[dict] = None

    class Config:
        from_attributes = True

