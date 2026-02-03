from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.v1.api import api_router
from app.core.database import Base, engine
from app.db import models  # noqa: F401

app = FastAPI(
    title="FastAPI Backend",
    description="FastAPI backend for Vue 3 frontend",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix="/api/v1")


@app.on_event("startup")
def on_startup():
    """初始化数据库表"""

    Base.metadata.create_all(bind=engine)


@app.get("/")
async def root():
    return {"message": "FastAPI Backend is running"}


@app.get("/health")
async def health_check():
    return {"status": "healthy"}
