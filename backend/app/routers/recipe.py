from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app import models, database, schemas

router = APIRouter(
    prefix="/recipes",
    tags=["recipes"],
    responses={404: {"description": "Not found"}},
)

@router.get("/{recipe_id}") # schemas.RecipeDetailResponse 필요
def get_recipe_detail(recipe_id: int, db: Session = Depends(database.get_db)):
    recipe = db.query(models.Recipe).filter(models.Recipe.recipe_id == recipe_id).first()
    if not recipe:
        raise HTTPException(status_code=404, detail="레시피를 찾을 수 없습니다.")

    # 재료 목록 조회
    ingredients = []
    for ri in recipe.ingredients:
        ingredients.append({
            "product_id": ri.product_id,
            "name": ri.product.name,
            "quantity_info": ri.quantity_info,
            "image_url": ri.product.image_url,
        })
        
    return {
        "recipe_id": recipe.recipe_id,
        "title": recipe.title,
        "description": recipe.description,
        "instructions": recipe.instructions, # 긴 텍스트
        "image_url": recipe.image_url,
        "cooking_time_min": 30, # DB 컬럼 없음, 임시값
        "difficulty": "보통",   # DB 컬럼 없음, 임시값
        "ingredients": ingredients
    }
