from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import desc, asc
from typing import List

from .. import models, schemas, database
from ..dependencies import get_current_user

router = APIRouter(
    prefix="/api/recommendations",
    tags=["recommendations"],
)

@router.get("/by-product/{product_id}", response_model=List[schemas.RecipeRecommendResponse])
def recommend_recipes_ai(
    product_id: int, 
    cart_session_id: int = None, # 내 장바구니랑 비교하려면 필요
    db: Session = Depends(database.get_db)
):
    """
    [AI 추천 로직]
    1. 선택한 상품(product_id)의 임베딩 벡터를 가져옵니다.
    2. pgvector를 사용해 해당 상품과 '의미적으로 가장 가까운' 레시피를 찾습니다.
    3. (옵션) 현재 장바구니에 없는 부족한 재료를 계산해서 알려줍니다.
    """
    
    # 1. 상품 조회 (벡터 포함)
    target_product = db.query(models.Product).filter(models.Product.product_id == product_id).first()
    if not target_product:
        raise HTTPException(status_code=404, detail="상품을 찾을 수 없습니다.")

    # 2. AI 추천 쿼리 작성
    # embedding이 있는 경우: 코사인 거리(Cosine Distance)로 유사도 정렬
    # embedding이 없는 경우: 단순히 해당 재료를 포함하는 레시피 검색 (Fallback)
    
    if target_product.embedding is not None:
        # 🔥 핵심: pgvector의 <=> 연산자 (Cosine Distance) 사용
        # 상품의 벡터와 레시피의 벡터 거리가 가까울수록 상위에 노출
        recommendations = (
            db.query(models.Recipe)
            .order_by(models.Recipe.embedding.cosine_distance(target_product.embedding))
            .limit(5)
            .all()
        )
    else:
        # 벡터가 없으면 기존처럼 '재료 포함 여부'로 검색 (Hard Rule)
        recommendations = (
            db.query(models.Recipe)
            .join(models.RecipeIngredient)
            .filter(models.RecipeIngredient.product_id == product_id)
            .limit(5)
            .all()
        )

    # 3. 장바구니 비교를 위한 내 아이템 조회
    my_owned_product_ids = set()
    if cart_session_id:
        my_items = db.query(models.CartItem).filter(models.CartItem.cart_session_id == cart_session_id).all()
        my_owned_product_ids = {item.product_id for item in my_items}
        # 방금 찍은 상품도 포함
        my_owned_product_ids.add(product_id)

    # 4. 응답 데이터 조립 (부족한 재료 계산)
    results = []
    for recipe in recommendations:
        # 이 레시피의 모든 재료 가져오기
        recipe_ingredients = db.query(models.RecipeIngredient).filter(
            models.RecipeIngredient.recipe_id == recipe.recipe_id
        ).all()
        
        missing_list = []
        for ri in recipe_ingredients:
            # 주재료(Product) 정보 가져오기
            ing_product = ri.product 
            is_owned = ing_product.product_id in my_owned_product_ids
            
            if not is_owned:
                missing_list.append({
                    "product_id": ing_product.product_id,
                    "name": ing_product.name,
                    "is_owned": False
                })

        # 결과 추가
        results.append({
            "recipe_id": recipe.recipe_id,
            "title": recipe.title,
            "description": recipe.description,
            "image_url": recipe.image_url,
            # AI 유사도 점수가 있으면 넣고 아니면 0 (embedding이 없을 수도 있으므로)
            "similarity_score": 0.0, # 계산하려면 쿼리에서 distance 컬럼을 select 해야 함 (복잡도 때문에 생략하거나 추후 고도화)
            "missing_ingredients": missing_list
        })

    return results