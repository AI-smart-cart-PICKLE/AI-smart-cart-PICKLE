from sqlalchemy.orm import Session
from fastapi import HTTPException
from app.models import CartSession, CartItem, Product

# 오차 허용 
TOLERANCE_RATE = 0.05  # 5%

# 무게 검증
def validate_cart_weight(
    db: Session,
    cart_session_id: int,
    measured_weight_g: int
) -> dict:
    cart = db.query(CartSession).filter(
        CartSession.cart_session_id == cart_session_id
    ).first()

    items = db.query(CartItem).join(Product).filter(
        CartItem.cart_session_id == cart_session_id
    ).all()

    expected_weight = sum(
        item.quantity * item.product.unit_weight_g
        for item in items
    )

    difference = measured_weight_g - expected_weight
    tolerance = int(expected_weight * TOLERANCE_RATE)

    if abs(difference) <= tolerance:
        status = "MATCH"
        message = "무게 검증 통과. 결제 가능합니다."
    elif difference > 0:
        status = "OVER_WEIGHT"
        message = "무게가 초과되었습니다. 상품 수량을 변경하거나 상품을 추가해 주세요."
    else:
        status = "UNDER_WEIGHT"
        message = "무게가 부족합니다. 상품을 삭제하거나 수량을 변경해 주세요."

    cart.expected_total_g = expected_weight
    cart.measured_total_g = measured_weight_g

    return {
        "is_valid": status == "MATCH",
        "status": status,
        "expected_weight": expected_weight,
        "measured_weight": measured_weight_g,
        "difference": difference,
        "tolerance": tolerance,
        "message": message
    }
