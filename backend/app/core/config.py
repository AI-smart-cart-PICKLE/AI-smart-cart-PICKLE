import os
from dotenv import load_dotenv
from pathlib import Path

# 프로젝트 루트(S14P11A202/) 폴더를 기준으로 .env 파일을 찾습니다.
# app/core/config.py -> parent(1): app/core -> parent(2): app -> parent(3): backend -> parent(4): 프로젝트 루트
BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent
load_dotenv(BASE_DIR / ".env")


class Settings:
    DATABASE_URL = os.getenv("DATABASE_URL")
    GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
    GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")
    GOOGLE_REDIRECT_URI = os.getenv("GOOGLE_REDIRECT_URI")
    KAKAO_REST_API_KEY = os.getenv("KAKAO_REST_API_KEY")
    KAKAO_REDIRECT_URI = os.getenv("KAKAO_REDIRECT_URI") 
    KAKAO_ADMIN_KEY = os.getenv("KAKAO_ADMIN_KEY")
    JETSON_BASE_URL = os.getenv("JETSON_BASE_URL")
    JETSON_STREAM_URL = os.getenv("JETSON_STREAM_URL")

    BASE_URL = os.getenv("BASE_URL", "http://localhost:8000")
    SECRET_KEY = os.getenv("SECRET_KEY", "dev_secret_key_change_me_in_production")

settings = Settings()



