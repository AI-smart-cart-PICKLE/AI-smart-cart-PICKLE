from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from .. import models, schemas, database
from ..dependencies import get_current_user 
from sqlalchemy.sql import func 
import requests
from app.core.config import settings
from datetime import datetime
import uuid

from app.schemas import (
    CartWeightValidateRequest,
    CartWeightValidateResponse
)
from app.utils.check_data import validate_cart_weight

router = APIRouter(
    prefix="/carts",
    tags=["carts"],
    responses={404: {"description": "Not found"}},
)

# QR pair
@router.post("/pair/qr")
def pair_cart_by_qr(
    device_code: str,
    db: Session = Depends(database.get_db),
    current_user: models.AppUser = Depends(get_current_user),
):
    # 1. 입력값 정제 (하이픈을 언더바로 변경하여 DB 매칭 확률 높임)
    clean_code = device_code.strip().replace('-', '_')
    
    # 2. 디바이스 조회
    device = (
        db.query(models.CartDevice)
        .filter((models.CartDevice.device_code == device_code) | (models.CartDevice.device_code == clean_code))
        .first()
    )

    if not device:
        # 디버깅을 위해 가능한 모든 디바이스 출력 (로그)
        all_devices = db.query(models.CartDevice.device_code).all()
        raise HTTPException(
            status_code=404, 
            detail=f"카트 디바이스를 찾을 수 없습니다. (입력: {device_code}, 정제: {clean_code}, 가용: {[d[0] for d in all_devices]})"
        )

    # 3. [추가] 사용자의 기존 활성 세션 모두 종료 (중복 연동 방지)
    db.query(models.CartSession).filter(
        models.CartSession.user_id == current_user.user_id,
        models.CartSession.status == models.CartSessionStatus.ACTIVE
    ).update({"status": models.CartSessionStatus.CANCELLED, "ended_at": func.now()})
    db.flush()

    # 4. 해당 디바이스의 ACTIVE 세션 조회
    session = (
        db.query(models.CartSession)
        .filter(
            models.CartSession.cart_device_id == device.cart_device_id,
            models.CartSession.status == models.CartSessionStatus.ACTIVE,
        )
        .order_by(models.CartSession.started_at.desc())
        .first()
    )

    # 5. 없으면 새 세션 생성
    if not session:
        session = models.CartSession(
            cart_device_id=device.cart_device_id,
            user_id=current_user.user_id,
            status=models.CartSessionStatus.ACTIVE,
        )
        db.add(session)
        print(f"DEBUG: Created NEW session {session.cart_session_id} for user {current_user.user_id} on device {device.device_code}")
    else:
        # 6. 있으면 사용자만 연결
        session.user_id = current_user.user_id
        print(f"DEBUG: Re-assigned EXISTING session {session.cart_session_id} to user {current_user.user_id}")
    
    db.commit()
    db.refresh(session)

    return {
        "cart_session_id": session.cart_session_id,
        "cart_device_id": device.cart_device_id,
        "message": "카트가 앱과 연결되었습니다.",
    }

# --- 카트 연동 상태 확인 (웹 키오스크 폴링용) ---
@router.get("/pair/status/{device_code}")
def check_pairing_status(
    device_code: str,
    db: Session = Depends(database.get_db)
):
    # 1. 디바이스 조회 (유연한 검색)
    clean_code = device_code.strip().replace('-', '_')
    device = (
        db.query(models.CartDevice)
        .filter((models.CartDevice.device_code == device_code) | (models.CartDevice.device_code == clean_code))
        .first()
    )
    
    if not device:
        raise HTTPException(status_code=404, detail="Unknown Device")

    # 2. 해당 디바이스의 ACTIVE 세션 중 유저가 할당된 세션 찾기
    session = db.query(models.CartSession).filter(
        models.CartSession.cart_device_id == device.cart_device_id,
        models.CartSession.status == models.CartSessionStatus.ACTIVE,
        models.CartSession.user_id.isnot(None)
    ).first()

    if session:
        return {
            "paired": True,
            "cart_session_id": session.cart_session_id,
            "user_id": session.user_id
        }
    
    return {"paired": False}


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
@router.get("/current", response_model=schemas.CartSessionResponse)
def get_current_cart_session(
    db: Session = Depends(database.get_db),
    current_user: models.AppUser = Depends(get_current_user)
):
    """
    현재 로그인된 사용자의 활성 장바구니 세션을 조회합니다.
    없으면 404를 반환합니다.
    """
    session = db.query(models.CartSession).filter(
        models.CartSession.user_id == current_user.user_id,
        models.CartSession.status == models.CartSessionStatus.ACTIVE
    ).order_by(models.CartSession.cart_session_id.desc()).first()

    if not session:
        raise HTTPException(status_code=404, detail="활성화된 장바구니가 없습니다.")
    
    # 기존 get_cart_session 로직 재사용 가능하게 분리하면 좋지만 
    # 일단 여기에 구현
    response_items = []
    total_amount = 0
    total_quantity = 0

    for item in session.items:
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
        "expected_total_g": session.expected_total_g,
        "device_code": session.device.device_code if session.device else None
    }


# --- 2.1 특정 ID로 장바구니 조회 ---
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
        "expected_total_g": session.expected_total_g,
        "device_code": session.device.device_code if session.device else None
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


# 무게 검증
@router.post("/weight/validate", response_model=CartWeightValidateResponse)
def validate_weight(
    request: CartWeightValidateRequest,
    db: Session = Depends(database.get_db),
    current_user: models.AppUser = Depends(get_current_user)
):
    session = db.query(models.CartSession).filter(
        models.CartSession.cart_session_id == request.cart_session_id,
        models.CartSession.user_id == current_user.user_id
    ).first()

    if not session:
        raise HTTPException(status_code=404, detail="장바구니 세션을 찾을 수 없습니다.")

    result = validate_cart_weight(
        db=db,
        cart_session_id=request.cart_session_id,
        measured_weight_g=request.measured_weight_g
    )

    db.commit()
    return result


# --- 카트 세션 취소 ---
@router.post("/{session_id}/cancel")
def cancel_cart_session(
    session_id: int,
    db: Session = Depends(database.get_db),
    current_user: models.AppUser = Depends(get_current_user)
):
    session = db.query(models.CartSession).filter(
        models.CartSession.cart_session_id == session_id,
        models.CartSession.user_id == current_user.user_id
    ).first()

    if not session:
        raise HTTPException(status_code=404, detail="카트 세션을 찾을 수 없습니다.")

    if session.status != models.CartSessionStatus.ACTIVE:
        raise HTTPException(
            status_code=400,
            detail="취소 가능한 카트 상태가 아닙니다."
        )

    session.status = models.CartSessionStatus.CANCELLED
    session.ended_at = func.now()

    db.commit()

    return {
        "message": "카트 세션이 취소되었습니다.",
        "cart_session_id": session.cart_session_id,
        "status": session.status.value
    }


# --- 무게 검증 및 결제 요청 (Checkout) ---
@router.post("/{session_id}/checkout")
def checkout_cart_session(
    session_id: int,
    db: Session = Depends(database.get_db)
):
    """
    웹 키오스크(카트)에서 '결제하기' 버튼을 눌렀을 때 호출됩니다.
    세션 상태를 CHECKOUT_REQUESTED로 변경하여 모바일 앱에 알림을 줍니다.
    """
    session = db.query(models.CartSession).filter(
        models.CartSession.cart_session_id == session_id
    ).first()

    if not session:
        raise HTTPException(status_code=404, detail="카트 세션을 찾을 수 없습니다.")

    if session.status != models.CartSessionStatus.ACTIVE:
        raise HTTPException(status_code=400, detail="결제 요청이 가능한 상태가 아닙니다.")

    # 상태 변경
    session.status = models.CartSessionStatus.CHECKOUT_REQUESTED
    db.commit()

    return {
        "message": "결제 요청이 완료되었습니다. 모바일 앱에서 결제를 진행해 주세요.",
        "cart_session_id": session.cart_session_id,
        "status": session.status.value
    }


# 카메라 뷰 on
@router.post("/{cart_session_id}/camera/view/on")
def camera_view_on(
    cart_session_id: int,
    db: Session = Depends(database.get_db),
    current_user: models.AppUser = Depends(get_current_user),
):
    cart = (
        db.query(models.CartSession)
        .filter(
            models.CartSession.cart_session_id == cart_session_id,
            models.CartSession.user_id == current_user.user_id,
            models.CartSession.status == models.CartSessionStatus.ACTIVE,
        )
        .first()
    )

    if not cart:
        raise HTTPException(status_code=404, detail="Active cart not found")

    cart.camera_view_on = True
    db.commit()

    return {
        "cart_session_id": cart_session_id,
        "camera_view_on": True,
        "stream_url": settings.JETSON_STREAM_URL
    }


# camera view close
@router.post("/{cart_session_id}/camera/view/off")
def camera_view_off(
    cart_session_id: int,
    db: Session = Depends(database.get_db),
    current_user: models.AppUser = Depends(get_current_user),
):
    cart = (
        db.query(models.CartSession)
        .filter(
            models.CartSession.cart_session_id == cart_session_id,
            models.CartSession.user_id == current_user.user_id,
            models.CartSession.status == models.CartSessionStatus.ACTIVE,
        )
        .first()
    )

    if not cart:
        raise HTTPException(status_code=404, detail="Active cart not found")

    cart.camera_view_on = False
    db.commit()

    return {
        "cart_session_id": cart_session_id,
        "camera_view_on": False
    }