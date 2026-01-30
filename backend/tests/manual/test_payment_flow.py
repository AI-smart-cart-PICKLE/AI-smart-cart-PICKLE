"""
[결제 로직 통합 테스트 스크립트 - 수정본]
이 스크립트는 새로운 '/api/payments/request' 엔드포인트를 중심으로
장바구니 무게 검증 및 결제 분기 처리를 테스트합니다.

기능:
1. 유저 생성 및 로그인
2. 테스트 상품(무게 100g) 생성
3. 장바구니에 상품 담기 (2개 -> 예상 무게 200g)
4. [테스트 1] 무게 불일치 시나리오 (150g 전송) -> 409 Conflict 예상
5. [테스트 2] 무게 일치 시나리오 (200g 전송) -> 200 OK 예상

실행 방법:
$ cd backend
$ python -m tests.manual.test_payment_flow
"""
import requests
import random
import string
import sys
import os

# --- 설정 ---
BASE_URL = "http://localhost:8000"
API_AUTH_SIGNUP = f"{BASE_URL}/api/auth/signup"
API_AUTH_LOGIN = f"{BASE_URL}/api/auth/login"
API_PAYMENT_REQUEST = f"{BASE_URL}/api/payments/request"

# --- 유틸리티 ---
def random_string(length=8):
    return ''.join(random.choices(string.ascii_lowercase + string.digits, k=length))

def create_random_user():
    email = f"test_{random_string()}@example.com"
    password = "TestPassword123!"
    nick_rand = ''.join(random.choices(string.ascii_lowercase, k=4))
    nickname = f"User{nick_rand}"
    
    print(f"🆕 회원가입 시도: {email}")
    requests.post(API_AUTH_SIGNUP, json={
        "email": email,
        "password": password,
        "nickname": nickname
    })
    return email, password

def login(email, password):
    res = requests.post(API_AUTH_LOGIN, json={"email": email, "password": password})
    if res.status_code != 200:
        print(f"❌ 로그인 실패: {res.text}")
        sys.exit(1)
    return res.json()["access_token"]

def ensure_test_product_exists():
    """테스트용 상품(100g, 1500원) 생성/조회"""
    sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
    from app.database import SessionLocal
    from app import models
    
    db = SessionLocal()
    try:
        # 테스트 카테고리 확인
        category = db.query(models.ProductCategory).filter_by(name="테스트카테고리").first()
        if not category:
            category = models.ProductCategory(name="테스트카테고리", zone_code="T-1")
            db.add(category)
            db.commit()

        # 테스트 상품 확인
        product_name = "테스트용 과자(100g)"
        product = db.query(models.Product).filter_by(name=product_name).first()
        
        if not product:
            print("📦 테스트 상품 생성 중...")
            new_product = models.Product(
                category_id=category.category_id,
                name=product_name,
                price=1500,
                unit_weight_g=100,  # 100g
                barcode=f"TEST{random.randint(1000,9999)}"
            )
            db.add(new_product)
            db.commit()
            db.refresh(new_product)
            return new_product.product_id
        
        return product.product_id
    except Exception as e:
        print(f"⚠️ DB 오류: {e}")
        sys.exit(1)
    finally:
        db.close()

def main():
    print("🚀 [결제/무게 검증 테스트] 시작합니다...")
    
    # 0. 준비
    product_id = ensure_test_product_exists() 
    email, password = create_random_user()
    token = login(email, password)
    headers = {"Authorization": f"Bearer {token}"}

    # 1. 카트 세션 준비
    sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
    from app.database import SessionLocal
    from app import models
    db = SessionLocal()
    
    device_code = "TEST_DEVICE_001"
    device = db.query(models.CartDevice).filter_by(device_code=device_code).first()
    if not device:
        device = models.CartDevice(device_code=device_code)
        db.add(device)
        db.commit()
        db.refresh(device)
    
    user_id = db.query(models.AppUser).filter_by(email=email).first().user_id
    
    # 기존 활성 세션 정리
    db.query(models.CartSession).filter_by(user_id=user_id, status=models.CartSessionStatus.ACTIVE).update({"status": models.CartSessionStatus.CANCELLED})
    db.commit()
    
    new_session = models.CartSession(
        cart_device_id=device.cart_device_id,
        user_id=user_id,
        status=models.CartSessionStatus.ACTIVE
    )
    db.add(new_session)
    db.commit()
    db.refresh(new_session)
    cart_session_id = new_session.cart_session_id
    db.close()
    
    print(f"✅ 세션 준비 완료: ID {cart_session_id}")

    # 2. 상품 담기 (100g * 2개 = 200g, 3000원)
    # 수정된 경로: /api/carts/{session_id}/items
    print(f"➕ 상품 담기 (ID: {product_id}, 2개)...")
    API_CART_ADD_ITEM = f"{BASE_URL}/api/carts/{cart_session_id}/items"
    res = requests.post(API_CART_ADD_ITEM, headers=headers, json={
        "product_id": product_id,
        "quantity": 2
    })
    if res.status_code != 200:
        print(f"❌ 상품 담기 실패: {res.status_code} - {res.text}")
        sys.exit(1)
    print("✅ 상품 담기 성공")

    # 3. [TEST CASE 1] 무게 불일치 테스트
    print("\n⚖️  [CASE 1] 무게 불일치 테스트 (예상 200g vs 측정 150g)")
    payload_fail = {
        "cart_session_id": cart_session_id,
        "measured_weight_g": 150,  
        "amount": 3000,
        "use_subscription": False
    }
    res = requests.post(API_PAYMENT_REQUEST, headers=headers, json=payload_fail)
    
    if res.status_code == 409:
        print("✅ 성공: 409 Conflict 응답 받음")
        print(f"   메시지: {res.json().get('message')}")
    else:
        print(f"❌ 실패: {res.status_code} (예상: 409)")
        print(f"   응답: {res.text}")

    # 4. [TEST CASE 2] 무게 일치 테스트
    print("\n⚖️  [CASE 2] 무게 일치 테스트 (예상 200g vs 측정 200g)")
    payload_success = {
        "cart_session_id": cart_session_id,
        "measured_weight_g": 200, 
        "amount": 3000,
        "use_subscription": False
    }
    res = requests.post(API_PAYMENT_REQUEST, headers=headers, json=payload_success)
    
    if res.status_code == 200:
        print("✅ 성공: 200 OK 응답 받음")
        print(f"   결과: {res.json()}")
    else:
        print(f"❌ 실패: {res.status_code} (예상: 200)")
        print(f"   응답: {res.text}")

    print("\n🏁 테스트 완료")

if __name__ == "__main__":
    main()
