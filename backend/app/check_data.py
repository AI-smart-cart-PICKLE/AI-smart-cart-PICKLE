# backend/check_data.py
from sqlalchemy import text
from app.database import SessionLocal
from app import models

def check_db():
    db = SessionLocal()
    try:
        print("====== 🔍 DB 데이터 점검 ======")
        
        # 1. 상품(Product) 확인
        products = db.query(models.Product).all()
        print(f"\n🧅 [상품] 총 {len(products)}개")
        for p in products:
            print(f" - ID: {p.product_id}, 이름: {p.name}")

        # 2. 레시피(Recipe) 확인
        recipes = db.query(models.Recipe).all()
        print(f"\n🍲 [레시피] 총 {len(recipes)}개")
        for r in recipes:
            print(f" - ID: {r.recipe_id}, 이름: {r.title}")

        # 3. 연결고리(RecipeIngredient) 확인 (여기가 핵심!)
        links = db.query(models.RecipeIngredient).all()
        print(f"\n🔗 [연결] 총 {len(links)}개")
        for l in links:
            print(f" - 레시피({l.recipe_id}) <-> 재료({l.product_id}) | 점수: {l.importance_score}")

        if not links:
            print("\n❌ 문제 발견: 상품과 레시피는 있는데 '연결' 데이터가 없네요!")
            print("   -> seed_data.py를 다시 실행해야 합니다.")
        else:
            print("\n✅ 데이터는 정상입니다. product_id를 다시 확인해보세요.")

    except Exception as e:
        print(f"❌ 에러 발생: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    check_db()