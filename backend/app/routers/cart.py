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


# 카트에 담긴 상품 목록 조회
@router.get("/{session_id}/items")
def get_cart_items(
    session_id: int,
    db: Session = Depends(database.get_db)
):
    session = (
        db.query(models.CartSession)
        .filter(models.CartSession.cart_session_id == session_id)
        .first()
    )

    if not session:
        raise HTTPException(status_code=404, detail="카트 세션을 찾을 수 없습니다.")

    items = (
        db.query(models.CartItem)
        .filter(models.CartItem.cart_session_id == session_id)
        .all()
    )

    total_price = 0
    total_expected_weight = 0

    item_list = []
    for item in items:
        item_total_price = item.unit_price * item.quantity
        item_expected_weight = item.product.unit_weight_g * item.quantity

        total_price += item_total_price
        total_expected_weight += item_expected_weight

        item_list.append({
            "cart_item_id": item.cart_item_id,
            "product_id": item.product.product_id,
            "name": item.product.name,
            "quantity": item.quantity,
            "unit_price": item.unit_price,
            "total_price": item_total_price,
            "unit_weight_g": item.product.unit_weight_g,
            "expected_weight_g": item_expected_weight,
            "image_url": item.product.image_url,
        })

    return {
        "cart_session_id": session_id,
        "status": session.status.value,
        "summary": {
            "total_price": total_price,
            "expected_total_g": total_expected_weight,
            "measured_total_g": session.measured_total_g,
            "weight_diff_g": session.measured_total_g - total_expected_weight,
        },
        "items": item_list,
    }
