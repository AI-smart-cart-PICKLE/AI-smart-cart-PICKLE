import requests
import urllib3
import sys
import random
import string
import json

# SSL 경고 무시
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

BASE_URL = "https://localhost/api"
HEADERS = {"Content-Type": "application/json"}
COOKIES = {}

# 상태 공유용 전역 변수
GLOBAL_STATE = {
    "user_email": "",
    "user_password": "",
    "access_token": None,
    "product_id": None,
    "recipe_id": None,
    "cart_session_id": None,
    "cart_item_id": None
}

def generate_random_email():
    return f"testuser_{''.join(random.choices(string.ascii_lowercase + string.digits, k=8))}@example.com"

def log(step, message, status="INFO"):
    icons = {"INFO": "ℹ️", "PASS": "✅", "FAIL": "❌", "WARN": "⚠️"}
    print(f"{icons.get(status, '')} [{step}] {message}")

def req(method, endpoint, payload=None, auth=False, expected_status=[200, 201]):
    url = f"{BASE_URL}{endpoint}"
    headers = HEADERS.copy()
    
    if auth and GLOBAL_STATE["access_token"]:
        headers["Authorization"] = f"Bearer {GLOBAL_STATE['access_token']}"

    try:
        if method == "GET":
            response = requests.get(url, headers=headers, cookies=COOKIES, verify=False, timeout=5)
        elif method == "POST":
            response = requests.post(url, headers=headers, cookies=COOKIES, json=payload, verify=False, timeout=5)
        elif method == "PATCH":
            response = requests.patch(url, headers=headers, cookies=COOKIES, json=payload, verify=False, timeout=5)
        elif method == "DELETE":
            response = requests.delete(url, headers=headers, cookies=COOKIES, json=payload, verify=False, timeout=5)
        elif method == "PUT":
            response = requests.put(url, headers=headers, cookies=COOKIES, json=payload, verify=False, timeout=5)
        
        if response.status_code in expected_status:
            log(f"{method} {endpoint}", f"Status: {response.status_code}", "PASS")
            return response.json() if response.content else {}
        else:
            log(f"{method} {endpoint}", f"Expected {expected_status}, Got {response.status_code}", "FAIL")
            try:
                print(f"   Response: {json.dumps(response.json(), indent=2)}")
            except:
                print(f"   Response: {response.text[:200]}")
            return None

    except Exception as e:
        log(f"{method} {endpoint}", f"Exception: {str(e)}", "FAIL")
        return None

def main():
    print(f"🚀 Full Smoke Test Started via {BASE_URL}\n")
    
    # 1. Health & Docs
    req("GET", "/health")
    
    # 2. Auth Flow
    print("\n--- [Auth Flow] ---")
    GLOBAL_STATE["user_email"] = generate_random_email()
    GLOBAL_STATE["user_password"] = "password123"
    
    # 회원가입
    res = req("POST", "/auth/signup", {
        "email": GLOBAL_STATE["user_email"],
        "password": GLOBAL_STATE["user_password"],
        "nickname": "Tester"
    })
    
    # 로그인
    if res:
        login_res = requests.post(
            f"{BASE_URL}/auth/login",
            json={"email": GLOBAL_STATE["user_email"], "password": GLOBAL_STATE["user_password"]},
            verify=False
        )
        if login_res.status_code == 200:
            data = login_res.json()
            GLOBAL_STATE["access_token"] = data["access_token"]
            COOKIES.update(login_res.cookies) # Refresh Token 쿠키 저장
            log("POST /auth/login", "Login Successful", "PASS")
        else:
            log("POST /auth/login", f"Login Failed: {login_res.status_code}", "FAIL")
            sys.exit(1)

    # 내 정보 조회
    user_info = req("GET", "/users/me", auth=True)
    user_id = user_info["user_id"] if user_info else 1
    
    # 닉네임 변경
    req("PATCH", "/users/me/nickname", {"nickname": "NewTester"}, auth=True)
    
    # 3. Product Flow
    print("\n--- [Product Flow] ---")
    products = req("GET", "/products/", auth=True) 
    
    if products and isinstance(products, list) and len(products) > 0:
        GLOBAL_STATE["product_id"] = products[0]["product_id"]
        log("Select Product", f"Picked Product ID: {GLOBAL_STATE['product_id']}", "INFO")
        
        # 상세 조회
        req("GET", f"/products/{GLOBAL_STATE['product_id']}", auth=True)
        # 위치 조회
        req("GET", f"/products/{GLOBAL_STATE['product_id']}/location", auth=True)
        # AI 추천 (pgvector)
        req("GET", f"/recommendations/by-product/{GLOBAL_STATE['product_id']}", auth=True)
        # Barcode 조회 (스팸 바코드)
        req("GET", "/products/barcode/8801000000001", auth=True)
    else:
        log("Product Check", "No products found in DB. Skipping dependent tests.", "WARN")

    # 4. Cart Flow
    print("\n--- [Cart Flow] ---")
    # 세션 생성 (주의: DB에 CartDevice 데이터가 있어야 성공함)
    cart_res = req("POST", "/carts/", auth=True)
    
    if cart_res:
        GLOBAL_STATE["cart_session_id"] = cart_res["cart_session_id"]
        sid = GLOBAL_STATE["cart_session_id"]
        
        # 카메라 뷰 제어
        req("POST", f"/carts/{sid}/camera/view/on", auth=True)
        req("POST", f"/carts/{sid}/camera/view/off", auth=True)

        # 상품이 있다면 담기 테스트
        if GLOBAL_STATE["product_id"]:
            # 아이템 추가
            req("POST", f"/carts/{sid}/items", {
                "product_id": GLOBAL_STATE["product_id"],
                "quantity": 2
            }, auth=True)
            
            # 장바구니 조회 (담겼는지 확인)
            cart_detail = req("GET", f"/carts/{sid}", auth=True)
            if cart_detail and cart_detail.get("items"):
                GLOBAL_STATE["cart_item_id"] = cart_detail["items"][0]["cart_item_id"]
                
                # 수량 변경
                req("PATCH", f"/carts/items/{GLOBAL_STATE['cart_item_id']}", {"quantity": 5}, auth=True)
                
                # 무게 검증
                req("POST", "/carts/weight/validate", {
                    "cart_session_id": sid,
                    "measured_weight_g": 500
                }, auth=True)

                # 아이템 삭제 (Cleanup)
                req("DELETE", f"/carts/items/{GLOBAL_STATE['cart_item_id']}", auth=True)

        # 카트 취소
        req("POST", f"/carts/{sid}/cancel", auth=True)

    # 5. AI & Admin Flow (NEW)
    print("\n--- [AI & Admin Flow] ---")
    
    # 5-1. AI Training Trigger (Admin)
    # AI 서버 연결 실패(503)도 성공으로 간주 (Test 목적: 라우터 도달 여부)
    req("POST", "/admin/train", {
        "epochs": 1,
        "experiment_name": "smoke_test_augmented",
        "model_name": "yolo11n.pt",
        "mosaic": 0.5,
        "mixup": 0.1
    }, auth=True, expected_status=[200, 503, 500])

    # 5-2. AI Edge Sync (Cart)
    # 실제 디바이스가 보내는 요청 시뮬레이션
    req("POST", "/carts/sync-by-device", {
        "device_code": "CART-DEVICE-001",
        "items": [
            {"product_name": "신라면", "quantity": 1},
            {"product_name": "스팸 200g", "quantity": 2}
        ]
    }, expected_status=[200])


    # 6. Payment & Ledger Flow (Read-Only)
    print("\n--- [Payment & Ledger Flow] ---")
    req("GET", "/payments/methods", auth=True)
    
    # 가계부 (수정: user_id 쿼리 추가)
    req("GET", f"/ledger?user_id={user_id}", auth=True)
    req("GET", "/ledger/calendar?year=2026&month=2", auth=True)
    req("GET", "/ledger/summary/monthly?year=2026&month=2", auth=True)
    req("GET", "/ledger/top-categories?year=2026&month=2", auth=True)

    # 7. Recipe Flow (Read-Only)
    print("\n--- [Recipe Flow] ---")
    # 레시피 ID 1번 조회 시도 (없으면 404)
    req("GET", "/recipes/1", auth=True, expected_status=[200, 404])

    # 8. Cleanup (Withdraw)
    print("\n--- [Cleanup] ---")
    req("DELETE", "/users/me", auth=True, payload={"password": GLOBAL_STATE["user_password"]})
    req("POST", "/auth/logout", auth=True)

    print("\n🏁 Smoke Test Completed.")

if __name__ == "__main__":
    main()