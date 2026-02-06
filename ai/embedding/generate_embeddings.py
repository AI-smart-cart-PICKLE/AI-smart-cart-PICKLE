import os
import sys
import numpy as np
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from openai import OpenAI
from dotenv import load_dotenv
from pathlib import Path

# 프로젝트 루트의 .env 파일 로드
BASE_DIR = Path(__file__).resolve().parent.parent.parent
load_dotenv(BASE_DIR / ".env")

# DB 및 GMS API 설정
DATABASE_URL = os.getenv("DATABASE_URL")
GMS_KEY = os.getenv("GMS_KEY") # Authorization: Bearer $GMS_KEY 에 해당

# GMS 프록시 엔드포인트 설정
# curl 예시: https://gms.ssafy.io/gmsapi/api.openai.com/v1/embeddings
GMS_BASE_URL = "https://gms.ssafy.io/gmsapi/api.openai.com/v1"

if not DATABASE_URL:
    print("❌ DATABASE_URL이 .env에 설정되어 있지 않습니다.")
    sys.exit(1)

if not GMS_KEY:
    print("❌ GMS_KEY가 .env에 설정되어 있지 않습니다.")
    sys.exit(1)

# GMS 전용 클라이언트 초기화
client = OpenAI(
    api_key=GMS_KEY,
    base_url=GMS_BASE_URL
)

def get_embedding(text_content, model="text-embedding-3-small"):
    """
    GMS 프록시를 통해 OpenAI 임베딩을 생성합니다.
    """
    if not text_content:
        return None
    
    clean_text = text_content.replace("\n", " ").strip()
    try:
        response = client.embeddings.create(input=[clean_text], model=model)
        return response.data[0].embedding
    except Exception as e:
        print(f"❌ 임베딩 생성 실패: {e}")
        return None

def update_product_embeddings():
    db = SessionLocal()
    try:
        products = db.execute(text("SELECT product_id, name, product_info FROM product WHERE embedding IS NULL")).fetchall()
        print(f"📦 상품 임베딩 작업 시작 (대상: {len(products)}개)")
        
        for prod in products:
            product_id, name, info = prod
            display_name = (info or {}).get("display_name", "")
            brand = (info or {}).get("brand", "")
            content = f"상품명: {name}, 브랜드: {brand}, 표시명: {display_name}"
            
            embedding = get_embedding(content)
            if embedding:
                # pgvector 컬럼 업데이트를 위해 문자열 형태로 변환
                db.execute(
                    text("UPDATE product SET embedding = :emb WHERE product_id = :id"),
                    {"emb": str(embedding), "id": product_id}
                )
                print(f"✅ 상품 ID {product_id} ({name}) 완료")
        db.commit()
    except Exception as e:
        print(f"❌ 상품 오류: {e}")
        db.rollback()
    finally:
        db.close()

def update_recipe_embeddings():
    db = SessionLocal()
    try:
        recipes = db.execute(text("SELECT recipe_id, title, description, instructions FROM recipe WHERE embedding IS NULL")).fetchall()
        print(f"🍳 레시피 임베딩 작업 시작 (대상: {len(recipes)}개)")
        
        for rec in recipes:
            recipe_id, title, desc, inst = rec
            content = f"제목: {title}, 설명: {desc or ''}, 조리법: {inst or ''}"
            
            embedding = get_embedding(content)
            if embedding:
                db.execute(
                    text("UPDATE recipe SET embedding = :emb WHERE recipe_id = :id"),
                    {"emb": str(embedding), "id": recipe_id}
                )
                print(f"✅ 레시피 ID {recipe_id} ({title}) 완료")
        db.commit()
    except Exception as e:
        print(f"❌ 레시피 오류: {e}")
        db.rollback()
    finally:
        db.close()

# SQLAlchemy 연결 설정 유지
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

if __name__ == "__main__":
    print(f"🚀 GMS 엔드포인트를 사용한 임베딩 생성 프로세스 시작")
    print(f"📍 Endpoint: {GMS_BASE_URL}")
    update_product_embeddings()
    update_recipe_embeddings()
    print("✨ 모든 작업이 완료되었습니다.")
