import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.concurrency import asynccontextmanager
from app.db.database import Base, async_engine
from app.routers import user, song, playlist

# main.py : FastAPI 애플리케이션 진입점
# 애플리케이션 인스턴스 생성, 미들웨어 설정, 라우터 포함
# 애플리케이션 수명 주기(lifespan)동안 데이터베이스 테이블을 생성

@asynccontextmanager
async def lifespan(app: FastAPI):
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    await async_engine.dispose()

app=FastAPI(lifespan=lifespan)

# 미들웨어 등록


# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],    # 모든 도메인 요청 허용
    allow_credentials=True,   # 자격 증명 true일 경우에만 응답 노출
    allow_methods=["*"],      # 모든 http 메소드 허용
    allow_headers=["*"],      # 모든 헤더 허용
)

# 라우터 등록
app.include_router(user.router)
app.include_router(song.router)
app.include_router(playlist.router)