import datetime
import sys
import os
from dotenv import load_dotenv

# Add parent directory to path to allow importing 'app'
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Load environment variables
load_dotenv(os.path.join(os.path.dirname(__file__), '../.env'))

from sqlalchemy import text  # ★ 이 줄 꼭 추가하세요!
from app.database import SessionLocal, engine
from app import models

def init_data():
    # ★ [핵심] DB에 벡터 기능을 강제로 켭니다.
    try:
        with engine.connect() as conn:
            conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
            conn.commit()
            print("✅ pgvector 기능 활성화 완료!")
    except Exception as e:
        print(f"⚠️ 벡터 기능 활성화 경고: {e}")

    # 1. 테이블 생성
    models.Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    try:
        print("🌱 데이터 심는 중...")

        # 2. 테스트 유저 생성
        user = models.AppUser(user_id=1, email="test@test.com", nickname="테스트유저", provider="LOCAL")
        db.merge(user)

        # 3. 상품 생성 (양파)
        onion = models.Product(product_id=100, name="양파", price=500, unit_weight_g=200)
        db.merge(onion)

        # 4. 레시피 생성 (양파수프)
        soup = models.Recipe(recipe_id=501, title="프렌치 어니언 수프", description="양파가 듬뿍 들어간 수프")
        db.merge(soup)

        # 5. 상품-레시피 연결 (가중치 5점!)
        link = models.RecipeIngredient(recipe_id=501, product_id=100, importance_score=5, quantity_info="2개")
        db.merge(link)
        
        # 6. 카트 기기 & 세션 생성
        device = models.CartDevice(cart_device_id=99, device_code="CART_001")
        db.merge(device)
        
        session = models.CartSession(
            cart_session_id=1, 
            cart_device_id=99, 
            user_id=1, 
            status=models.CartSessionStatus.ACTIVE
        )
        db.merge(session)

        db.commit()
        print("✅ 기초 데이터 생성 완료! (User:1, Product:100, Session:1)")

    except Exception as e:
        print(f"❌ 에러 발생: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    init_data()