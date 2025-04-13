from fastapi import FastAPI
from app.routers.traitmatcher_router import router as traitmatcher_router
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# (선택) CORS 미들웨어 추가 – 프론트엔드 연결 시 꼭 필요
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 개발 중에는 전체 허용
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 라우터 등록
app.include_router(traitmatcher_router, prefix="/matching", tags=["Matching"])

# 기본 상태 확인용 엔드포인트
@app.get("/")
async def root():
    return {"message": "FastAPI server is running"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
