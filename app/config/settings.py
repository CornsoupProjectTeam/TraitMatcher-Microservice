import os
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

class Settings:
    SECRET_KEY: str = os.getenv("SECRET_KEY")
    KAFKA_URL: str = os.getenv("KAFKA_URL")
    DATABASE_URL: str = os.getenv("DB_URL")

settings = Settings()

# 환경변수 없을 경우 오류 발생
if not settings.SECRET_KEY or not settings.KAFKA_URL or not settings.DATABASE_URL:
    raise RuntimeError("필수 환경변수 설정이 누락되었습니다.")

# Async DB 연결 설정
engine = create_async_engine(
    settings.DATABASE_URL,
    echo=True,   # 개발 중이면 True (쿼리 출력), 배포 시 False
)

AsyncSessionLocal = sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False
)
