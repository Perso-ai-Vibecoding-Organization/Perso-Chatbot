from fastapi import FastAPI
from api.routers.auth import router as auth_router
from api.routers.chatbot import router as chatbot_router
from api.core.database import Base, engine
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://perso-fe.vercel.app"],  # 프론트 주소
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
# 테이블 생성
Base.metadata.create_all(bind=engine)

app.include_router(auth_router, prefix="/auth")
app.include_router(chatbot_router, prefix="/api/chat")
