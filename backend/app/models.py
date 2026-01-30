from sqlalchemy import (
    Column, Integer, String, TIMESTAMP, ForeignKey, DateTime, Boolean, Text, Numeric, Date, Enum as SAEnum
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from sqlalchemy.dialects.postgresql import JSONB
from pgvector.sqlalchemy import Vector
import enum
from app.db.base import Base


# --- Enums (DB Enum Types) ---

class UserProvider(enum.Enum):
    LOCAL = "LOCAL"
    GOOGLE = "GOOGLE"
    KAKAO = "KAKAO"

class CartSessionStatus(enum.Enum):
    ACTIVE = "ACTIVE"
    CHECKOUT_REQUESTED = "CHECKOUT_REQUESTED"
    PAID = "PAID"
    CANCELLED = "CANCELLED"

class DetectionActionType(enum.Enum):
    ADD = "ADD"
    REMOVE = "REMOVE"

class PaymentMethodType(enum.Enum):
    CARD = "CARD"
    KAKAO_PAY = "KAKAO_PAY"

class PgProviderType(enum.Enum):
    KAKAO_PAY = "KAKAO_PAY"
    CARD_PG = "CARD_PG"

class PaymentStatus(enum.Enum):
    PENDING = "PENDING"
    APPROVED = "APPROVED"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"

class LedgerCategory(enum.Enum):
    GROCERY = "GROCERY"
    MEAT = "MEAT"
    DAIRY = "DAIRY"
    BEVERAGE = "BEVERAGE"
    SNACK = "SNACK"
    HOUSEHOLD = "HOUSEHOLD"
    ETC = "ETC"

# --- Models ---

class AppUser(Base):
    __tablename__ = "app_user"

    user_id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, nullable=False)
    provider = Column(SAEnum(UserProvider), nullable=False, default=UserProvider.LOCAL)
    nickname = Column(String(40), nullable=False)
    password_hash = Column(String(255))
    created_at = Column(DateTime(timezone=True), nullable=False, default=func.now())
    updated_at = Column(DateTime(timezone=True), default=func.now(), onupdate=func.now())
    is_active = Column(Boolean, nullable=False, default=True)
    deleted_at = Column(DateTime(timezone=True), nullable=True)

    # Relationships
    saved_recipes = relationship("SavedRecipe", back_populates="user", cascade="all, delete-orphan")
    cart_sessions = relationship("CartSession", back_populates="user")
    payment_methods = relationship("PaymentMethod", back_populates="user", cascade="all, delete-orphan")
    payments = relationship("Payment", back_populates="user")
    ledger_entries = relationship("LedgerEntry", back_populates="user", cascade="all, delete-orphan")


class PasswordResetToken(Base):
    __tablename__ = "password_reset_token"

    token = Column(String, primary_key=True)
    user_id = Column( Integer, ForeignKey("app_user.user_id"), nullable=False)

    expires_at = Column(TIMESTAMP, nullable=False)
    used = Column(Boolean, default=False)

    created_at = Column(TIMESTAMP, server_default=func.now())


class ProductCategory(Base):
    __tablename__ = "product_category"

    category_id = Column(Integer, primary_key=True, index=True)
    name = Column(String(60), unique=True, nullable=False)
    zone_code = Column(String(30), nullable=False)

    # Relationships
    products = relationship("Product", back_populates="category")


class Product(Base):
    __tablename__ = "product"

    product_id = Column(Integer, primary_key=True, index=True)
    category_id = Column(Integer, ForeignKey("product_category.category_id"), nullable=False)
    barcode = Column(String(64), unique=True)
    name = Column(String(255), nullable=False)
    price = Column(Integer, nullable=False)
    unit_weight_g = Column(Integer, nullable=False)
    stock_quantity = Column(Integer, default=0)
    image_url = Column(Text)
    product_info = Column(JSONB)
    embedding = Column(Vector(1536))
    created_at = Column(DateTime(timezone=True), default=func.now())

    # Relationships
    category = relationship("ProductCategory", back_populates="products")
    cart_items = relationship("CartItem", back_populates="product")
    detection_logs = relationship("CartDetectionLog", back_populates="product")
    recipe_ingredients = relationship("RecipeIngredient", back_populates="product")


class Recipe(Base):
    __tablename__ = "recipe"

    recipe_id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    description = Column(Text)
    instructions = Column(Text)
    image_url = Column(Text)

    embedding = Column(Vector(1536))
    created_at = Column(DateTime(timezone=True), default=func.now())

    # Relationships
    ingredients = relationship("RecipeIngredient", back_populates="recipe", cascade="all, delete-orphan")
    saved_by_users = relationship("SavedRecipe", back_populates="recipe", cascade="all, delete-orphan")


class RecipeIngredient(Base):
    __tablename__ = "recipe_ingredient"

    recipe_id = Column(Integer, ForeignKey("recipe.recipe_id", ondelete="CASCADE"), primary_key=True)
    product_id = Column(Integer, ForeignKey("product.product_id"), primary_key=True)
    quantity_info = Column(String(50))
    importance_score = Column(Integer, default=1)

    # Relationships
    recipe = relationship("Recipe", back_populates="ingredients")
    product = relationship("Product", back_populates="recipe_ingredients")


class SavedRecipe(Base):
    __tablename__ = "saved_recipe"

    user_id = Column(Integer, ForeignKey("app_user.user_id", ondelete="CASCADE"), primary_key=True)
    recipe_id = Column(Integer, ForeignKey("recipe.recipe_id", ondelete="CASCADE"), primary_key=True)
    saved_at = Column(DateTime(timezone=True), default=func.now())

    # Relationships
    user = relationship("AppUser", back_populates="saved_recipes")
    recipe = relationship("Recipe", back_populates="saved_by_users")


class CartDevice(Base):
    __tablename__ = "cart_device"

    cart_device_id = Column(Integer, primary_key=True, index=True)
    device_code = Column(String(64), unique=True, nullable=False)

    # Relationships
    sessions = relationship("CartSession", back_populates="device")
    logs = relationship("CartDetectionLog", back_populates="device")


class CartSession(Base):
    __tablename__ = "cart_session"

    cart_session_id = Column(Integer, primary_key=True, index=True)
    cart_device_id = Column(Integer, ForeignKey("cart_device.cart_device_id"), nullable=False)
    user_id = Column(Integer, ForeignKey("app_user.user_id"))
    status = Column(SAEnum(CartSessionStatus), nullable=False, default=CartSessionStatus.ACTIVE)
    budget_limit = Column(Integer, default=0)
    expected_total_g = Column(Integer, default=0)
    measured_total_g = Column(Integer, default=0)
    started_at = Column(DateTime(timezone=True), nullable=False, default=func.now())
    ended_at = Column(DateTime(timezone=True))
    camera_view_on = Column(Boolean, default=False, nullable=False)

    # Relationships
    device = relationship("CartDevice", back_populates="sessions")
    user = relationship("AppUser", back_populates="cart_sessions")
    items = relationship("CartItem", back_populates="session", cascade="all, delete-orphan")
    logs = relationship("CartDetectionLog", back_populates="session", cascade="all, delete-orphan")
    payment = relationship("Payment", uselist=False, back_populates="session")


class CartItem(Base):
    __tablename__ = "cart_item"

    cart_item_id = Column(Integer, primary_key=True, index=True)
    cart_session_id = Column(Integer, ForeignKey("cart_session.cart_session_id", ondelete="CASCADE"), nullable=False)
    product_id = Column(Integer, ForeignKey("product.product_id"), nullable=False)
    quantity = Column(Integer, nullable=False, default=1)
    unit_price = Column(Integer, nullable=False)
    added_at = Column(DateTime(timezone=True), default=func.now())

    # Relationships
    session = relationship("CartSession", back_populates="items")
    product = relationship("Product", back_populates="cart_items")


class CartDetectionLog(Base):
    __tablename__ = "cart_detection_log"

    log_id = Column(Integer, primary_key=True, index=True)
    cart_session_id = Column(Integer, ForeignKey("cart_session.cart_session_id", ondelete="CASCADE"), nullable=False)
    cart_device_id = Column(Integer, ForeignKey("cart_device.cart_device_id"), nullable=False)
    product_id = Column(Integer, ForeignKey("product.product_id"))
    action_type = Column(SAEnum(DetectionActionType), nullable=False)
    confidence_score = Column(Numeric(5, 2))
    detected_weight_g = Column(Integer)
    is_applied = Column(Boolean, default=False)
    detected_at = Column(DateTime(timezone=True), default=func.now())
    created_at = Column(DateTime(timezone=True), default=func.now())

    # Relationships
    session = relationship("CartSession", back_populates="logs")
    device = relationship("CartDevice", back_populates="logs")
    product = relationship("Product", back_populates="detection_logs")


class PaymentMethod(Base):
    __tablename__ = "payment_method"

    method_id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("app_user.user_id", ondelete="CASCADE"), nullable=False)
    method_type = Column(SAEnum(PaymentMethodType), nullable=False)
    billing_key = Column(String(255))
    card_brand = Column(String(30))
    card_last4 = Column(String(4))
    is_default = Column(Boolean, nullable=False, default=False)
    created_at = Column(DateTime(timezone=True), default=func.now())

    # Relationships
    user = relationship("AppUser", back_populates="payment_methods")
    payments = relationship("Payment", back_populates="method")


class Payment(Base):
    __tablename__ = "payment"

    payment_id = Column(Integer, primary_key=True, index=True)
    cart_session_id = Column(Integer, ForeignKey("cart_session.cart_session_id"), unique=True)
    user_id = Column(Integer, ForeignKey("app_user.user_id"), nullable=False)
    method_id = Column(Integer, ForeignKey("payment_method.method_id"))
    pg_provider = Column(SAEnum(PgProviderType), nullable=False)
    pg_tid = Column(String(255))
    status = Column(SAEnum(PaymentStatus), nullable=False, default=PaymentStatus.PENDING)
    total_amount = Column(Integer, nullable=False)
    approved_at = Column(DateTime(timezone=True))

    # Relationships
    session = relationship("CartSession", back_populates="payment")
    user = relationship("AppUser", back_populates="payments")
    method = relationship("PaymentMethod", back_populates="payments")
    ledger_entries = relationship("LedgerEntry", back_populates="payment")


class LedgerEntry(Base):
    __tablename__ = "ledger_entry"

    ledger_entry_id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("app_user.user_id", ondelete="CASCADE"), nullable=False)
    payment_id = Column(Integer, ForeignKey("payment.payment_id", ondelete="SET NULL"))
    spend_date = Column(Date, nullable=False)
    category = Column(SAEnum(LedgerCategory), nullable=False, default=LedgerCategory.ETC)
    amount = Column(Integer, nullable=False)
    memo = Column(Text)

    # Relationships
    user = relationship("AppUser", back_populates="ledger_entries")
    payment = relationship("Payment", back_populates="ledger_entries")
