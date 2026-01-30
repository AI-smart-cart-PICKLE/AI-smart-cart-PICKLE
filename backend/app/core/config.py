import os
from dotenv import load_dotenv
from pathlib import Path

# backend/ 폴더를 기준으로 .env 파일을 찾습니다.
# app/core/config.py -> parent: app/core -> parent: app -> parent: backend
BASE_DIR = Path(__file__).resolve().parent.parent.parent
load_dotenv(BASE_DIR / ".env")


class Settings:
    DATABASE_URL = os.getenv("DATABASE_URL")
    GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
    GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")
    GOOGLE_REDIRECT_URI = os.getenv("GOOGLE_REDIRECT_URI")
    KAKAO_REST_API_KEY = os.getenv("KAKAO_REST_API_KEY")
    KAKAO_REDIRECT_URI = os.getenv("KAKAO_REDIRECT_URI")   


settings = Settings()



