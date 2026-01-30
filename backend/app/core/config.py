import os
from dotenv import load_dotenv
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[3]
load_dotenv(BASE_DIR / ".env")


class Settings:
    DATABASE_URL = os.getenv("DATABASE_URL")
    GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
    GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")
    GOOGLE_REDIRECT_URI = os.getenv("GOOGLE_REDIRECT_URI")
    KAKAO_REST_API_KEY = os.getenv("KAKAO_REST_API_KEY")
    KAKAO_REDIRECT_URI = os.getenv("KAKAO_REDIRECT_URI") 
    JETSON_BASE_URL = os.getenv("JETSON_BASE_URL")
    JETSON_STREAM_URL = os.getenv("JETSON_STREAM_URL")

settings = Settings()



