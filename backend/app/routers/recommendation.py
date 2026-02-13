# app/routers/recommendation.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app import schemas, database
from app.services.recommendation_service import RecommendationService

router = APIRouter(
    prefix="/recommendations",
    tags=["recommendations"],
    responses={404: {"description": "Not found"}},
)

@router.get("/by-cart/{cart_session_id}", response_model=List[schemas.RecipeRecommendResponse])
def recommend_recipes_by_cart(
    cart_session_id: int,
    db: Session = Depends(database.get_db)
):
    """
    [장바구니 기반 AI 추천]
    - Service Layer(RecommendationService)로 로직을 위임하여 처리합니다.
    - Fat Controller 문제를 해결하고 비즈니스 로직을 분리했습니다.
    """
    service = RecommendationService(db)
    return service.recommend_by_cart(cart_session_id)

@router.get("/by-product/{product_id}", response_model=List[schemas.RecipeRecommendResponse])
def recommend_recipes_ai(
    product_id: int, 
    cart_session_id: int = None, 
    db: Session = Depends(database.get_db)
):
    """
    [단일 상품 기반 AI 추천]
    - 선택한 상품과 유사한 레시피를 추천합니다.
    """
    service = RecommendationService(db)
    return service.recommend_by_product(product_id, cart_session_id)