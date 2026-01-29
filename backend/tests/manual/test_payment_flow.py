"""
[결제 전체 프로세스 테스트 스크립트 - Part 1]
이 스크립트는 회원가입 -> 로그인 -> 장바구니 생성 -> 상품 담기 -> 결제 준비(Ready)까지의 흐름을 검증합니다.

기능:
1. 랜덤 유저 생성 및 로그인 (토큰 발급)
2. 테스트용 상품 생성 (DB에 없을 경우)
3. 장바구니 세션 생성 및 상품 담기
4. 카카오페이 결제 준비 API 호출 -> 결제 URL(TID) 발급

실행 방법:
$ cd backend
$ python -m tests.manual.test_payment_flow
"""
import requests
import random
import string
import time
import sys
import os

# --- 설정 ---
BASE_URL = "http://localhost:8000"
API_AUTH_SIGNUP = f"{BASE_URL}/api/auth/signup"
API_AUTH_LOGIN = f"{BASE_URL}/api/auth/login"
API_CART_CREATE = f"{BASE_URL}/api/carts/"
API_PAYMENT_READY = f"{BASE_URL}/api/payments/ready"

# --- 유틸리티 ---
def random_string(length=8):
    return ''.join(random.choices(string.ascii_lowercase + string.digits, k=length))

def create_random_user():
    email = f"test_{random_string()}@example.com"
    password = "TestPassword123!"
    # 닉네임은 숫자 제외 (정규식 규칙 준수)
    letters = string.ascii_lowercase
    nick_rand = ''.join(random.choices(letters, k=4))
    nickname = f"User{nick_rand}"
    
    print(f"🆕 회원가입 시도: {email} / {nickname}")
    res = requests.post(API_AUTH_SIGNUP, json={
        "email": email,
        "password": password,
        "nickname": nickname
    })
    
    if res.status_code != 200 and res.status_code != 201:
        print(f"❌ 회원가입 실패: {res.text}")
        sys.exit(1)
        
    return email, password

def login(email, password):
    print(f"🔑 로그인 시도...")
    res = requests.post(API_AUTH_LOGIN, json={
        "email": email,
        "password": password
    })
    
    if res.status_code != 200:
        print(f"❌ 로그인 실패: {res.text}")
        sys.exit(1)
        
    token = res.json()["access_token"]
    print(f"✅ 로그인 성공! Token 획득 완료.")
    return token

def ensure_test_product_exists():
    """
    상품이 하나도 없으면 테스트 진행이 불가능하므로,
    DB에 직접 접근해서 상품을 하나 넣습니다.
    (서버가 실행 중인 상태여야 함)
    """
    sys.path.append(os.path.dirname(os.path.abspath(__file__)))
    from app.database import SessionLocal
    from app import models
    
    db = SessionLocal()
    try:
        product = db.query(models.Product).first()
        if not product:
            print("📦 상품이 없어 테스트용 상품을 생성합니다...")
            category = models.ProductCategory(name="테스트카테고리", zone_code="A-1")
            db.add(category)
            db.commit()
            
            new_product = models.Product(
                category_id=category.category_id,
                name="맛있는 테스트 우유",
                price=1500,
                unit_weight_g=1000,
                barcode="8801111222233"
            )
            db.add(new_product)
            db.commit()
            db.refresh(new_product)
            print(f"✅ 테스트 상품 생성 완료: ID {new_product.product_id}")
            return new_product.product_id
        else:
            print(f"ℹ️ 기존 상품 사용: ID {product.product_id} ({product.name})")
            return product.product_id
    except Exception as e:
        print(f"⚠️ DB 연결 실패 또는 상품 확인 중 오류: {e}")
        print("상품 담기 단계에서 오류가 날 수 있습니다.")
        return 1
    finally:
        db.close()

def main():
    print("🚀 [결제 테스트 스크립트] 시작합니다...")
    
    # 0. 상품 준비
    product_id = ensure_test_product_exists()

    # 1. 유저 생성 및 로그인
    email, password = create_random_user()
    token = login(email, password)
    headers = {"Authorization": f"Bearer {token}"}

    # 2. 장바구니 세션 생성
    print("🛒 장바구니 세션 생성 중...")
    res = requests.post(API_CART_CREATE, headers=headers)
    if res.status_code != 200:
        print(f"❌ 장바구니 생성 실패: {res.text}")
        sys.exit(1)
    
    cart_session = res.json()
    cart_id = cart_session["cart_session_id"]
    print(f"✅ 장바구니 생성 완료: ID {cart_id}")

    # 3. 상품 담기
    print(f"➕ 상품 담기 (ID: {product_id}, 가격: 1500원)...")
    add_item_url = f"{BASE_URL}/api/carts/{cart_id}/items"
    res = requests.post(add_item_url, headers=headers, json={
        "product_id": product_id,
        "quantity": 2  # 2개 담기 (총 3000원)
    })
    
    if res.status_code != 200:
        print(f"❌ 상품 담기 실패: {res.text}")
        sys.exit(1)
    print("✅ 상품 담기 성공")

    # 4. 결제 준비 요청 (Ready)
    print("💳 결제 준비(Ready) 요청 중...")
    res = requests.post(API_PAYMENT_READY, headers=headers, json={
        "cart_session_id": cart_id,
        "total_amount": 3000, # 1500 * 2
        "method_id": None
    })

    if res.status_code != 200:
        print(f"❌ 결제 준비 실패: {res.text}")
        sys.exit(1)
    
    payment_data = res.json()
    tid = payment_data['tid']
    pc_url = payment_data.get('next_redirect_pc_url')
    
    print("\n" + "="*50)
    print(f"🎉 결제 준비 성공! TID: {tid}")
    print(f"👉 아래 URL을 클릭해서 [카카오페이 결제]를 진행하세요:")
    print(f"\n{pc_url}\n")
    print("="*50)
    print("ℹ️ 결제를 완료하면 서버 콘솔에 '승인' 로그가 찍힐 것입니다.")
    print("ℹ️ 결제 승인 API 호출 테스트는 브라우저 결제 완료 후 진행되어야 하므로 여기서는 URL 발급까지만 검증합니다.")

if __name__ == "__main__":
    main()
