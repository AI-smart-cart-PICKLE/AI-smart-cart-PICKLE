# app/core/redis_client.py
import redis
import os
from dotenv import load_dotenv

load_dotenv()  # .env 파일 로드

# 1. 환경변수에서 Redis 접속 정보 가져오기
# 로컬에서 돌릴 땐 'localhost', Docker Compose로 돌릴 땐 'redis' 컨테이너 이름 사용
REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))
REDIS_DB = int(os.getenv("REDIS_DB", 0))

# 2. Redis 클라이언트 생성 (Connection Pool 방식 사용)
# decode_responses=True : 바이트(b'string')가 아니라 문자열('string')로 받기 위함 (필수!)
pool = redis.ConnectionPool(
    host=REDIS_HOST,
    port=REDIS_PORT,
    db=REDIS_DB,
    decode_responses=True
)

def get_redis():
    """
    FastAPI의 Depends(get_redis)로 주입하기 위한 제너레이터
    """
    client = redis.Redis(connection_pool=pool)
    try:
        yield client
    finally:
        client.close()