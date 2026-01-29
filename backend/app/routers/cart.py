from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from .. import models, schemas, database
from ..dependencies import get_current_user 

router = APIRouter(
    prefix="/api/carts",
    tags=["carts"],
    responses={404: {"description": "Not found"}},
)

# --- 1. 장바구니 생성 (쇼핑 시작) ---
@router.post("/", response_model=schemas.CartSessionResponse)
def create_cart_session(
    db: Session = Depends(database.get_db),
    current_user: models.AppUser = Depends(get_current_user)
):
    """
    새로운 장바구니 세션을 생성합니다.
    """
    new_session = models.CartSession(
        user_id=current_user.user_id,
        status=models.CartSessionStatus.ACTIVE,
        cart_device_id=1  # 테스트용 임시 디바이스 ID
    )
    db.add(new_session)
    db.commit()
    db.refresh(new_session)
    
    # 빈 장바구니 반환
    return {
        "cart_session_id": new_session.cart_session_id,
        "status": new_session.status.value,
        "total_amount": 0,
        "items": [],
        "expected_total_g": 0
    }


# --- 2. 장바구니 조회 ---
@router.get("/{session_id}", response_model=schemas.CartSessionResponse)
def get_cart_session(
    session_id: int, 
    db: Session = Depends(database.get_db),
    current_user: models.AppUser = Depends(get_current_user)
):
    # 세션 본인 확인
    session = db.query(models.CartSession).filter(
        models.CartSession.cart_session_id == session_id,
        models.CartSession.user_id == current_user.user_id
    ).first()

    if not session:
        raise HTTPException(status_code=404, detail="장바구니를 찾을 수 없습니다.")
    
    # 상품 목록 가져오기
    cart_items = db.query(models.CartItem).filter(
        models.CartItem.cart_session_id == session_id
    ).all()

    response_items = []
    total_amount = 0
    total_quantity = 0

    for item in cart_items:
        item_total = item.unit_price * item.quantity
        total_amount += item_total
        total_quantity += item.quantity
        
        response_items.append({
            "cart_item_id": item.cart_item_id,
            "product": item.product, 
            "quantity": item.quantity,
            "unit_price": item.unit_price,
            "total_price": item_total 
        })

    return {
        "cart_session_id": session.cart_session_id,
        "status": session.status.value, 
        "total_amount": total_amount,
        "total_items": total_quantity,
        "items": response_items,        
        "expected_total_g": session.expected_total_g
    }


# --- 3. 장바구니에 상품 담기 ---
@router.post("/{session_id}/items")
def add_cart_item(
    session_id: int,
    item_req: schemas.CartItemCreate,
    db: Session = Depends(database.get_db),
    current_user: models.AppUser = Depends(get_current_user)
):
    # 세션 본인 확인
    session = db.query(models.CartSession).filter(
        models.CartSession.cart_session_id == session_id,
        models.CartSession.user_id == current_user.user_id
    ).first()
    if not session:
        raise HTTPException(status_code=404, detail="장바구니 세션이 없습니다.")

    # 상품 존재 확인
    product = db.query(models.Product).filter(models.Product.product_id == item_req.product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="상품이 존재하지 않습니다.")

    # 이미 담긴 상품인지 확인
    existing_item = db.query(models.CartItem).filter(
        models.CartItem.cart_session_id == session_id,
        models.CartItem.product_id == item_req.product_id
    ).first()

    if existing_item:
        existing_item.quantity += item_req.quantity
    else:
        new_item = models.CartItem(
            cart_session_id=session_id,
            product_id=item_req.product_id,
            quantity=item_req.quantity,
            unit_price=product.price
        )
        db.add(new_item)
    
    # 예상 무게 업데이트
    if session.expected_total_g is None:
        session.expected_total_g = 0
    
    unit_weight = product.unit_weight_g or 0
    session.expected_total_g += (unit_weight * item_req.quantity)

    db.commit()
    return {"message": "장바구니에 상품을 담았습니다."}


# --- 요리 선택 ---
@router.post("/{session_id}/select-recipe")
def select_recipe(session_id: int, recipe_id: int, db: Session = Depends(database.get_db)):
    session = db.query(models.CartSession).filter(models.CartSession.cart_session_id == session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="세션을 찾을 수 없습니다.")
    
    return {"detail": f"레시피(ID:{recipe_id})가 선택되었습니다."}