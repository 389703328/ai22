from fastapi import APIRouter
from app.api.v1.endpoints import auth, users, ai, knowledge, skills

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(ai.router, prefix="/ai", tags=["ai"])
api_router.include_router(knowledge.router, tags=["knowledge"])
api_router.include_router(skills.router, tags=["skills"])
