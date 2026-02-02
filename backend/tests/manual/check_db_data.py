"""
[DB 데이터 검증 스크립트]
이 스크립트는 특정 유저의 이메일을 기반으로 관련 DB 데이터가 정상적으로 생성되었는지 확인합니다.
SQLAlchemy를 사용하여 DB에 직접 접속합니다.

검증 항목:
1. 유저 정보 (User)
2. 장바구니 세션 상태 (CartSession) - PAID 여부
3. 결제 내역 (Payment) - APPROVED 여부
4. 가계부 내역 (LedgerEntry) - 생성 여부

실행 방법:
스크립트 하단의 verify_data("이메일") 부분을 수정한 뒤 실행하세요.
$ python -m tests.manual.check_db_data
"""
import sys
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app import models
from app.db.base import Base

# DB 연결 설정
SQLALCHEMY_DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://admin:password123@localhost:5432/postgres")
if os.getenv("DB_PASSWORD"): # 환경변수에 비번이 따로 있으면 조합 (일반적인 경우 .env에서 로드됨)
    pass 

engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)
db = SessionLocal()

def verify_data(email):
    print(f"🔍 '{email}' 유저 데이터 조회 중...\n")

    # 1. 유저 찾기
    user = db.query(models.AppUser).filter(models.AppUser.email == email).first()
    if not user:
        print("❌ 유저를 찾을 수 없습니다.")
        return

    print(f"👤 유저 ID: {user.user_id}, 닉네임: {user.nickname}")

    # 2. 카트 세션 확인
    cart = db.query(models.CartSession).filter(
        models.CartSession.user_id == user.user_id,
        models.CartSession.status == models.CartSessionStatus.PAID
    ).order_by(models.CartSession.cart_session_id.desc()).first()
    
    if cart:
        print(f"🛒 [완료된 장바구니] ID: {cart.cart_session_id}, 상태: {cart.status.value}, 종료시간: {cart.ended_at}")
    else:
        print("⚠️ 완료된(PAID) 장바구니 세션이 없습니다.")

    # 3. 결제 내역 확인
    payment = db.query(models.Payment).filter(models.Payment.user_id == user.user_id).order_by(models.Payment.payment_id.desc()).first()
    if payment:
        print(f"💳 [결제 내역] ID: {payment.payment_id}, TID: {payment.pg_tid}, 금액: {payment.total_amount}원, 상태: {payment.status.value}")
    else:
        print("⚠️ 결제 내역이 없습니다.")

    # 4. 가계부 내역 확인 (메모 컬럼 제외하고 조회)
    # models.LedgerEntry 전체를 조회하면 스키마 불일치로 에러가 발생하므로 필요한 필드만 조회
    ledger = db.query(
        models.LedgerEntry.ledger_entry_id,
        models.LedgerEntry.spend_date,
        models.LedgerEntry.amount,
        models.LedgerEntry.category
    ).filter(models.LedgerEntry.user_id == user.user_id).order_by(models.LedgerEntry.ledger_entry_id.desc()).first()

    if ledger:
        # 튜플로 반환되므로 인덱스나 이름으로 접근 불가할 수 있어 단순 출력
        print(f"📔 [가계부] ID: {ledger.ledger_entry_id}, 날짜: {ledger.spend_date}, 금액: {ledger.amount}원, 카테고리: {ledger.category.value}")
    else:
        print("⚠️ 가계부 내역이 없습니다.")

if __name__ == "__main__":
    verify_data("test_fy97rs9d@example.com")
