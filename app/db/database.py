from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from app.core.settings import settings

# database.py : 데이터베이스 연결 및 세션 관리 모듈
# SQLAlchemy를 사용하여 비동기 및 동기 데이터베이스 엔진과 세션 로컬을 설정.

# 비동기 엔진 설정
async_engine = create_async_engine(settings.db_url, echo=False)

# 비동기 세션 설정
AsyncSessionLocal = sessionmaker(
    autocommit=False, autoflush=False, bind=async_engine, class_=AsyncSession
)

# 동기 엔진 설정
sync_engine = create_engine(settings.sync_db_url, pool_pre_ping=True)

# 기본 클래스 설정 (Base)
Base = declarative_base()

# 비동기 세션 생성기
async def get_db():
    async with AsyncSessionLocal() as session:
        yield session