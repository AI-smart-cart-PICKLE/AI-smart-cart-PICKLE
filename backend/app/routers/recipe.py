from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from .. import models, schemas, database

router = APIRouter(
    prefix="/api/recipes",
    tags=["recipes"],
)

@router.get("/{recipe_id}", response_model=schemas.RecipeDetailResponse)
def get_recipe_detail(
    recipe_id: int, 
    db: Session = Depends(database.get_db)
):
    """
    레시피 상세 조회
    - 레시피 기본 정보
    - 포함된 재료 목록 (Product 정보 포함)
    """
    recipe = db.query(models.Recipe).filter(models.Recipe.recipe_id == recipe_id).first()
    if not recipe:
        raise HTTPException(status_code=404, detail="레시피를 찾을 수 없습니다.")

    # 재료 정보 조립
    ingredients_response = []
    for ri in recipe.ingredients:
        ingredients_response.append({
            "product_id": ri.product_id,
            "name": ri.product.name,
            "quantity_info": ri.quantity_info,
            "image_url": ri.product.image_url
        })

    return {
        "recipe_id": recipe.recipe_id,
        "title": recipe.title,
        "description": recipe.description,
        "instructions": recipe.instructions,
        "image_url": recipe.image_url,
        "ingredients": ingredients_response
    }
