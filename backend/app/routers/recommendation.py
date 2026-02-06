from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import desc, asc
from typing import List

from .. import models, schemas, database
from ..dependencies import get_current_user
import logging

# 로거 설정
logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/recommendations",
    tags=["recommendations"],
    responses={404: {"description": "Not found"}},
)

import numpy as np

@router.get("/by-cart/{cart_session_id}", response_model=List[schemas.RecipeRecommendResponse])
def recommend_recipes_by_cart(
    cart_session_id: int,
    db: Session = Depends(database.get_db)
):
    """
    [장바구니 기반 AI 추천]
    1. 장바구니에 담긴 모든 상품의 임베딩 벡터 평균을 계산합니다.
    2. 평균 벡터와 가장 유사한 레시피를 추천합니다.
    3. 벡터가 없는 경우, 가장 많은 재료가 포함된 레시피를 추천합니다.
    """
    # 1. 카트 아이템 조회
    cart_items = db.query(models.CartItem).filter(models.CartItem.cart_session_id == cart_session_id).all()
    if not cart_items:
        logger.info(f"🛒 장바구니(Session {cart_session_id})가 비어있습니다.")
        return []

    logger.info(f"🔎 [추천 분석 시작] Session {cart_session_id} | 상품 {len(cart_items)}개 감지")

    # 2. 임베딩 벡터 수집 및 보유 상품 ID set 생성
    vectors = []
    my_owned_product_ids = {item.product_id for item in cart_items}
    
    for item in cart_items:
        has_embedding = item.product.embedding is not None
        emb_status = "✅O" if has_embedding else "❌X"
        logger.info(f"   - 상품: {item.product.name} (ID: {item.product_id}) | 임베딩: {emb_status}")
        
        if has_embedding:
            # pgvector 데이터는 이미 리스트 형태이므로 그대로 추가
            vectors.append(item.product.embedding)
            
    recommendations_query = []
    
    # 3. 추천 로직 실행
    if vectors:
        logger.info(f"🚀 [AI 모드] 유효 벡터 {len(vectors)}개로 Centroid 계산 및 추천 실행")
        # 벡터 평균 계산 (Centroid)
        avg_vector_np = np.mean(vectors, axis=0)
        # numpy float64를 일반 float 리스트로 변환 (DB 드라이버 호환성)
        avg_vector = [float(x) for x in avg_vector_np.tolist()]
        
        # Centroid와 유사한 레시피 검색 및 거리(Distance) 가져오기
        recommendations_query = (
            db.query(
                models.Recipe,
                models.Recipe.embedding.cosine_distance(avg_vector).label("distance")
            )
            .order_by("distance")
            .limit(5)
            .all()
        )
    else:
        logger.warning("⚠️ [Fallback 모드] 유효한 임베딩 벡터가 하나도 없습니다! 단순 가격순 추천을 실행합니다.")
        # 벡터 정보가 부족한 경우 Fallback
        sorted_items = sorted(cart_items, key=lambda x: x.unit_price, reverse=True)
        target_product_id = sorted_items[0].product_id
        logger.warning(f"   -> 기준 상품: {sorted_items[0].product.name} (가장 비쌈)")
        
        recommendations_query = [
            (r, 0.2) for r in db.query(models.Recipe)
            .join(models.RecipeIngredient)
            .filter(models.RecipeIngredient.product_id == target_product_id)
            .limit(5)
            .all()
        ]

    # 4. 응답 데이터 조립 (부족한 재료 계산)
    results = []
    for recipe, distance in recommendations_query:
        # 유사도 점수 계산: 1 - 거리 (거리가 0이면 100%, 1이면 0%)
        # text-embedding-3-small 모델의 경우 거리가 보통 0.3~0.7 사이에 분포함
        # UI에서 보기 좋게 0.5~1.0 사이로 스케일링하거나 보정 가능
        similarity = max(0, 1 - float(distance or 0.5))
        
        recipe_ingredients = db.query(models.RecipeIngredient).filter(
            models.RecipeIngredient.recipe_id == recipe.recipe_id
        ).all()
        
        all_ingredients = []
        missing_list = []
        
        for ri in recipe_ingredients:
            ing_product = ri.product 
            is_owned = ing_product.product_id in my_owned_product_ids
            
            all_ingredients.append({
                "product_id": ing_product.product_id,
                "name": ing_product.name,
                "is_owned": is_owned
            })
            
            if not is_owned:
                missing_list.append({
                    "product_id": ing_product.product_id,
                    "name": ing_product.name,
                    "is_owned": False
                })

        results.append({
            "recipe_id": recipe.recipe_id,
            "title": recipe.title,
            "description": recipe.description,
            "image_url": recipe.image_url,
            "similarity_score": similarity, 
            "ingredients": all_ingredients,  
            "missing_ingredients": missing_list
        })

    return results

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
        
        all_ingredients = []
        missing_list = []
        for ri in recipe_ingredients:
            # 주재료(Product) 정보 가져오기
            ing_product = ri.product 
            is_owned = ing_product.product_id in my_owned_product_ids
            
            # 전체 재료 리스트
            all_ingredients.append({
                "product_id": ing_product.product_id,
                "name": ing_product.name,
                "is_owned": is_owned
            })
            
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
            "ingredients": all_ingredients,  
            "missing_ingredients": missing_list
        })

    return results