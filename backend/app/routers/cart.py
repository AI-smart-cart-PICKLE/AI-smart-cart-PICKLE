from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from .. import models, database

router = APIRouter(
    prefix="/api/carts",
    tags=["carts"],
    responses={404: {"description": "Not found"}},
)

# 레시피 추천 API
@router.get("/recommendations")
def get_recommendations(product_id: int, db: Session = Depends(database.get_db)):
    """
    특정 재료(product_id)를 넣었을 때, 
    importance_score(중요도)가 높은 순서대로 레시피를 추천해줍니다.
    """
    recommendations = (
        db.query(models.Recipe)
        .join(models.RecipeIngredient)
        .filter(models.RecipeIngredient.product_id == product_id)
        .order_by(models.RecipeIngredient.importance_score.desc())
        .limit(4)
        .all()
    )
    
    if not recommendations:
        return {"detail": "관련된 추천 레시피가 없습니다."}
        
    return recommendations

# 요리 선택 API (앱 연동용)
@router.post("/{session_id}/select-recipe")
def select_recipe(session_id: int, recipe_id: int, db: Session = Depends(database.get_db)):
    session = db.query(models.CartSession).filter(models.CartSession.cart_session_id == session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="세션을 찾을 수 없습니다.")
    
    # 실제로는 여기서 세션 상태를 업데이트합니다.
    return {"detail": f"레시피(ID:{recipe_id})가 선택되었습니다."}