import os
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from kafka import KafkaProducer
import json

class Settings:
    def __init__(self):
        self.SECRET_KEY = os.getenv("SECRET_KEY")
        self.KAFKA_URL = os.getenv("KAFKA_URL")
        self.DATABASE_URL = os.getenv("DB_URL")

        if not self.SECRET_KEY or not self.KAFKA_URL or not self.DATABASE_URL:
            raise RuntimeError("필수 환경변수 설정이 누락되었습니다.")

        self.KAFKA_PRODUCER = KafkaProducer(
            bootstrap_servers=self.KAFKA_URL,
            value_serializer=lambda v: json.dumps(v, ensure_ascii=False).encode("utf-8"),
        )

        self.DB_ENGINE = create_async_engine(self.DATABASE_URL, echo=True)
        self.DB_SESSION: async_sessionmaker[AsyncSession] = async_sessionmaker(
            bind=self.DB_ENGINE,
            expire_on_commit=False,
        )

settings = Settings()