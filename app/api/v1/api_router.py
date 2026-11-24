from fastapi import APIRouter
from app.api.v1.endpoints import auth, orchestrator, summarize, threats

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])
api_router.include_router(
    orchestrator.router, prefix="/email", tags=["Email Operations"]
)
api_router.include_router(
    threats.router, prefix="/threats", tags=["AI Security Analysis"]
)
api_router.include_router(
    summarize.router, prefix="/ai", tags=["AI Summarization"]
)