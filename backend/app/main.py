from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text

from app.api.v1.api import api_router
from app.core.database import Base, engine
from fastapi import HTTPException as FastAPIHTTPException
from app.core.exceptions import (
    base_custom_exception_handler,
    http_exception_handler,
    generic_exception_handler,
    BaseCustomException,
)
from app.db import models  # noqa: F401

app = FastAPI(
    title="FastAPI Backend",
    description="FastAPI backend for Vue 3 frontend",
    version="1.0.0",
)

# Add exception handlers
app.add_exception_handler(BaseCustomException, base_custom_exception_handler)
app.add_exception_handler(FastAPIHTTPException, http_exception_handler)
app.add_exception_handler(Exception, generic_exception_handler)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:5173",
        "http://localhost:5180",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix="/api/v1")


@app.on_event("startup")
async def on_startup():
    """初始化数据库表"""

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        await conn.execute(
            text(
                "ALTER TABLE expert_knowledge_items "
                "ADD COLUMN IF NOT EXISTS sub_agent_id INTEGER"
            )
        )


@app.get("/")
async def root():
    return {"message": "FastAPI Backend is running"}


@app.get("/health")
async def health_check():
    return {"status": "healthy"}
