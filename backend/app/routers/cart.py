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
        "total_items": 0,
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
        db.add(models.CartItem(
            cart_session_id=session_id,
            product_id=item_req.product_id,
            quantity=item_req.quantity,
            unit_price=product.price
        ))

    db.flush()                      
    recalc_expected_weight(session) 
    db.commit()
    
    return {"message": "장바구니에 상품을 담았습니다."}


# --- AI 추론기 전용: 카트 상태 동기화 (Snapshot Sync) ---
@router.post("/sync-by-device")
def sync_cart_by_device(
    req: schemas.CartSyncRequest,
    db: Session = Depends(database.get_db)
):
    # 1. 기기 및 세션 조회
    device = db.query(models.CartDevice).filter(models.CartDevice.device_code == req.device_code).first()
    if not device:
        raise HTTPException(status_code=404, detail="Unknown Device")

    session = db.query(models.CartSession).filter(
        models.CartSession.cart_device_id == device.cart_device_id,
        models.CartSession.status == models.CartSessionStatus.ACTIVE
    ).first()
    if not session:
        raise HTTPException(status_code=404, detail="No Active Session")

    # 2. 기존 품목 싹 비우기 (동기화를 위해)
    db.query(models.CartItem).filter(models.CartItem.cart_session_id == session.cart_session_id).delete()

    # 3. 새로운 Snapshot으로 채우기
    synced_count = 0
    for item in req.items:
        product = db.query(models.Product).filter(models.Product.name == item.product_name).first()
        if product:
            db.add(models.CartItem(
                cart_session_id=session.cart_session_id,
                product_id=product.product_id,
                quantity=item.quantity,
                unit_price=product.price
            ))
            synced_count += 1
    
    db.flush()
    recalc_expected_weight(session)
    db.commit()
    return {"status": "synced", "item_count": synced_count}


# --- 요리 선택 ---
@router.post("/{session_id}/select-recipe")
def select_recipe(session_id: int, recipe_id: int, db: Session = Depends(database.get_db)):
    session = db.query(models.CartSession).filter(models.CartSession.cart_session_id == session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="세션을 찾을 수 없습니다.")
    
    # 실제로는 여기서 세션 상태를 업데이트합니다.
    return {"detail": f"레시피(ID:{recipe_id})가 선택되었습니다."}


# 예상 무게 계산
def recalc_expected_weight(session: models.CartSession):
    total_weight = 0
    for item in session.items:
        unit_weight = item.product.unit_weight_g or 0
        total_weight += unit_weight * item.quantity
    session.expected_total_g = total_weight


# 상품 삭제
@router.delete("/items/{cart_item_id}")
def delete_cart_item(
    cart_item_id: int,
    db: Session = Depends(database.get_db),
    current_user: models.AppUser = Depends(get_current_user)
):
    cart_item = (
        db.query(models.CartItem)
        .join(models.CartSession)
        .filter(
            models.CartItem.cart_item_id == cart_item_id,
            models.CartSession.user_id == current_user.user_id
        )
        .first()
    )

    if not cart_item:
        raise HTTPException(status_code=404, detail="카트 상품을 찾을 수 없습니다.")

    session = cart_item.session

    if session.status != models.CartSessionStatus.ACTIVE:
        raise HTTPException(status_code=400, detail="수정 가능한 카트 상태가 아닙니다.")

    db.delete(cart_item)
    db.flush()

    recalc_expected_weight(session)

    db.commit()

    return {
        "message": "상품이 카트에서 제거되었습니다.",
        "expected_total_g": session.expected_total_g
    }

# 상품 수량 변경
@router.patch("/items/{cart_item_id}")
def update_cart_item_quantity(
    cart_item_id: int,
    req: schemas.CartItemUpdate,
    db: Session = Depends(database.get_db),
    current_user: models.AppUser = Depends(get_current_user)
):
    # 1. 카트 상품 + 사용자 소유 확인
    cart_item = (
        db.query(models.CartItem)
        .join(models.CartSession)
        .filter(
            models.CartItem.cart_item_id == cart_item_id,
            models.CartSession.user_id == current_user.user_id
        )
        .first()
    )

    if not cart_item:
        raise HTTPException(status_code=404, detail="카트 상품을 찾을 수 없습니다.")

    session = cart_item.session

    # 2. 카트 상태 확인
    if session.status != models.CartSessionStatus.ACTIVE:
        raise HTTPException(status_code=400, detail="수정 가능한 카트 상태가 아닙니다.")

    # 3. 수량 변경
    cart_item.quantity = req.quantity

    db.flush()  # 변경사항 반영

    # 4. 예상 무게 재계산
    recalc_expected_weight(session)

    db.commit()
    db.refresh(cart_item)

    return {
        "message": "상품 수량이 변경되었습니다.",
        "cart_item_id": cart_item.cart_item_id,
        "quantity": cart_item.quantity,
        "expected_total_g": session.expected_total_g
    }
