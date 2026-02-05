from fastapi import APIRouter
from app.api.v1.endpoints import auth, users, ai, knowledge, skills, mcp, models, knowledge_graph, uploads, question_bank, session_library

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(ai.router, prefix="/ai", tags=["ai"])
api_router.include_router(knowledge.router, tags=["knowledge"])
api_router.include_router(skills.router, tags=["skills"])
api_router.include_router(mcp.router, prefix="/mcp", tags=["mcp"])
api_router.include_router(models.router, prefix="/models", tags=["models"])
api_router.include_router(knowledge_graph.router, tags=["knowledge-graph"])
api_router.include_router(uploads.router, tags=["uploads"])
api_router.include_router(question_bank.router, tags=["question-bank"])
api_router.include_router(session_library.router, tags=["session-library"])
