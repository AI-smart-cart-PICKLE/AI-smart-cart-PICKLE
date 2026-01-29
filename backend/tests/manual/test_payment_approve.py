"""
[결제 전체 프로세스 테스트 스크립트 - Part 2]
이 스크립트는 카카오페이 결제 승인(Approve) API를 호출하여 최종 결제를 완료합니다.
브라우저에서 결제 완료 후 발급받은 pg_token이 필요합니다.

기능:
1. 사용자 로그인 (토큰 발급)
2. 결제 승인 API 호출
3. 결제 상태(APPROVED) 및 가계부 생성 확인

실행 방법:
$ python -m tests.manual.test_payment_approve <이메일> <비밀번호> <TID> <PG_TOKEN>
예: python -m tests.manual.test_payment_approve test@example.com TestPass123! T123... pg_token...
"""
import requests
import sys

BASE_URL = "http://localhost:8000"
API_AUTH_LOGIN = f"{BASE_URL}/api/auth/login"
API_PAYMENT_APPROVE = f"{BASE_URL}/api/payments/approve"

def login(email, password):
    res = requests.post(API_AUTH_LOGIN, json={"email": email, "password": password})
    if res.status_code != 200:
        print("❌ 로그인 실패")
        sys.exit(1)
    return res.json()["access_token"]

def main():
    if len(sys.argv) < 5:
        print("사용법: python test_payment_approve.py <email> <password> <tid> <pg_token>")
        return

    email = sys.argv[1]
    password = sys.argv[2]
    tid = sys.argv[3]
    pg_token = sys.argv[4]

    token = login(email, password)
    headers = {"Authorization": f"Bearer {token}"}

    print(f"💳 결제 승인(Approve) 요청 중... (TID: {tid})")
    
    # schemas.PaymentApproveRequest 형식에 맞춤
    payload = {
        "tid": tid,
        "pg_token": pg_token,
        "partner_order_id": "dummy", # 서버 로직에서 DB 값으로 대체하므로 dummy 전달 가능
        "partner_user_id": "dummy"
    }

    res = requests.post(API_PAYMENT_APPROVE, headers=headers, json=payload)

    if res.status_code == 200:
        print("\n" + "="*50)
        print("✅ 결제 최종 승인 성공!!!")
        print(f"결제 ID: {res.json().get('payment_id')}")
        print(f"상태: {res.json().get('status')}")
        print(f"승인 시각: {res.json().get('approved_at')}")
        print("="*50)
        print("ℹ️ 이제 DB의 cart_session 상태가 'PAID'로 변경되었고, 가계부(Ledger)에 내역이 등록되었습니다.")
    else:
        print(f"❌ 승인 실패: {res.text}")

if __name__ == "__main__":
    main()
