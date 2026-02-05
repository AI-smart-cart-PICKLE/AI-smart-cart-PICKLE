import requests

def verify_kiosk_api_access():
    base_url = "http://localhost:8000/api"
    session_id = 1 # 테스트용 세션 ID
    
    print("--- 키오스크 API 접근 권한 테스트 (인증 토큰 없음) ---")
    
    # 1. 페어링 상태 확인 (성공 예상)
    print("\n1. 페어링 상태 확인 테스트 (GET /carts/pair/status/CART-DEVICE-001)")
    try:
        res = requests.get(f"{base_url}/carts/pair/status/CART-DEVICE-001")
        print(f"결과: {res.status_code}")
        print(f"응답: {res.text}")
    except Exception as e:
        print(f"네트워크 에러 (서버가 켜져있는지 확인): {e}")

    # 2. 장바구니 상세 조회 (실패 예상 - 현재 문제 지점)
    print(f"\n2. 장바구니 상세 조회 테스트 (GET /carts/{session_id})")
    try:
        res = requests.get(f"{base_url}/carts/{session_id}")
        print(f"결과: {res.status_code}")
        if res.status_code == 401:
            print("❌ 예상대로 '401 Unauthorized' 발생! 키오스크는 토큰이 없어서 조회가 거부됩니다.")
        elif res.status_code == 403:
            print("❌ '403 Forbidden' 발생! 인증 로직에 의해 차단되었습니다.")
        else:
            print(f"응답: {res.text}")
    except Exception as e:
        print(f"네트워크 에러 (서버가 켜져있는지 확인): {e}")

if __name__ == "__main__":
    verify_kiosk_api_access()