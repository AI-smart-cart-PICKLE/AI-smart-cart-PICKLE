# DB 테이블 정의 (SQLAlchemy - ERD 기반)
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from .database import Base

# 1. 상품 (재료)
class Product(Base):
    __tablename__ = "products"
    product_id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    price = Column(Integer)
    stock = Column(Integer)
    # ...기타 필드

# 2. 레시피 (요리)
class Recipe(Base):
    __tablename__ = "recipes"
    recipe_id = Column(Integer, primary_key=True, index=True)
    title = Column(String)
    description = Column(String)
    
    # N:M 관계 설정을 위한 연결
    ingredients = relationship("RecipeIngredient", back_populates="recipe")

# 3. [핵심] 레시피-재료 연결 (가중치 포함)
class RecipeIngredient(Base):
    __tablename__ = "recipe_ingredients"
    recipe_id = Column(Integer, ForeignKey("recipes.recipe_id"), primary_key=True)
    product_id = Column(Integer, ForeignKey("products.product_id"), primary_key=True)
    
    importance = Column(Integer, default=1) # ★ 추천 알고리즘의 핵심 (1~5점)
    quantity_info = Column(String) # 예: "반 개", "200g"

    recipe = relationship("Recipe", back_populates="ingredients")
    product = relationship("Product")

# 4. 결제 (Payment)
class Payment(Base):
    __tablename__ = "payments"
    payment_id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.user_id")) # User 모델 있다고 가정
    
    tid = Column(String, unique=True, index=True) # ★ 카카오페이 결제 고유 번호
    total_amount = Column(Integer)
    status = Column(String, default="READY") # READY, APPROVED, CANCELLED
    approved_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=func.now())