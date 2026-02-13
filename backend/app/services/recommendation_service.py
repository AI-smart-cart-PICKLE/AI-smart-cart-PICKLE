# app/services/recommendation_service.py
from sqlalchemy.orm import Session
from sqlalchemy import desc
from typing import List
import numpy as np
import logging

from app import models, schemas

logger = logging.getLogger(__name__)

class RecommendationService:
    def __init__(self, db: Session):
        self.db = db

    def recommend_by_cart(self, cart_session_id: int) -> List[dict]:
        """
        [장바구니 기반 AI 추천 비즈니스 로직]
        1. 카트 아이템 조회
        2. 임베딩 벡터 수집 및 평균 계산 (Centroid)
        3. 코사인 유사도 기반 레시피 검색 (Fallback: 재료 포함 여부)
        4. 응답 데이터 조립 (부족한 재료 마킹)
        """
        # 1. 카트 아이템 조회
        cart_items = self.db.query(models.CartItem).filter(
            models.CartItem.cart_session_id == cart_session_id
        ).all()
        
        if not cart_items:
            logger.info(f"🛒 장바구니(Session {cart_session_id})가 비어있습니다.")
            return []

        # 2. 벡터 수집
        vectors = []
        my_owned_product_ids = {item.product_id for item in cart_items}
        
        for item in cart_items:
            if item.product.embedding is not None:
                vectors.append(item.product.embedding)

        recommendations_query = []
        
        # 3. AI 추천 vs Fallback 분기 처리
        if vectors:
            logger.info(f"🚀 [AI 모드] 유효 벡터 {len(vectors)}개로 추천 실행")
            # 벡터 평균(Centroid) 계산
            avg_vector_np = np.mean(vectors, axis=0)
            avg_vector = [float(x) for x in avg_vector_np.tolist()]
            
            # 코사인 거리 순 정렬 (Distance가 작을수록 유사함)
            recommendations_query = (
                self.db.query(
                    models.Recipe,
                    models.Recipe.embedding.cosine_distance(avg_vector).label("distance")
                )
                .order_by("distance")
                .limit(5)
                .all()
            )
        else:
            logger.warning("⚠️ [Fallback 모드] 벡터 없음. 가격 기준 대체 추천 실행")
            # 가장 비싼 상품 기준
            sorted_items = sorted(cart_items, key=lambda x: x.unit_price, reverse=True)
            target_product_id = sorted_items[0].product_id
            
            # 단순 조인 검색 (distance를 임의로 0.2로 설정)
            recommendations_query = [
                (r, 0.2) for r in self.db.query(models.Recipe)
                .join(models.RecipeIngredient)
                .filter(models.RecipeIngredient.product_id == target_product_id)
                .limit(5)
                .all()
            ]

        # 4. 응답 데이터 조립
        return self._format_response(recommendations_query, my_owned_product_ids)

    def recommend_by_product(self, product_id: int, cart_session_id: int = None) -> List[dict]:
        """
        [단일 상품 기반 AI 추천 로직]
        """
        target_product = self.db.query(models.Product).filter(
            models.Product.product_id == product_id
        ).first()
        
        if not target_product:
            return []

        # AI 추천 쿼리
        if target_product.embedding is not None:
            recommendations = (
                self.db.query(
                    models.Recipe,
                    models.Recipe.embedding.cosine_distance(target_product.embedding).label("distance")
                )
                .order_by("distance")
                .limit(5)
                .all()
            )
        else:
            # Fallback
            recommendations_with_dummy_distance = [
                (r, 0.0) for r in self.db.query(models.Recipe)
                .join(models.RecipeIngredient)
                .filter(models.RecipeIngredient.product_id == product_id)
                .limit(5)
                .all()
            ]
            recommendations = recommendations_with_dummy_distance

        # 내 장바구니 정보 조회 (부족한 재료 계산용)
        my_owned_product_ids = set()
        if cart_session_id:
            my_items = self.db.query(models.CartItem).filter(
                models.CartItem.cart_session_id == cart_session_id
            ).all()
            my_owned_product_ids = {item.product_id for item in my_items}
        
        # 방금 찍은 상품도 '보유'로 처리
        my_owned_product_ids.add(product_id)

        # 포맷팅을 위해 (recipe, distance) 튜플 형태로 변환
        # (위에서 이미 튜플로 받았는지 체크 필요)
        if recommendations and isinstance(recommendations[0], models.Recipe):
             # AI 모드가 아닐 때 models.Recipe 객체만 반환된 경우 처리
             query_result = [(r, 0.0) for r in recommendations]
        else:
             query_result = recommendations
        
        return self._format_response(query_result, my_owned_product_ids)

    def _format_response(self, query_result, my_owned_ids: set) -> List[dict]:
        """
        [Helper] DB 결과를 API 응답 스키마에 맞게 변환하고 '부족한 재료'를 계산함
        """
        results = []
        for recipe, distance in query_result:
            # 유사도 점수 변환 (0~1)
            similarity = max(0, 1 - float(distance or 0.5))
            
            recipe_ingredients = self.db.query(models.RecipeIngredient).filter(
                models.RecipeIngredient.recipe_id == recipe.recipe_id
            ).all()
            
            all_ingredients = []
            missing_list = []
            
            for ri in recipe_ingredients:
                ing_product = ri.product 
                is_owned = ing_product.product_id in my_owned_ids
                
                ing_data = {
                    "product_id": ing_product.product_id,
                    "name": ing_product.name,
                    "is_owned": is_owned
                }
                all_ingredients.append(ing_data)
                
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