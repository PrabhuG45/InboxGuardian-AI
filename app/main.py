from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.v1.api_router import api_router

app = FastAPI(
    title="EasyMail Zero Trust AI Engine",
    description="Enterprise AI-Driven Email Security & Management Microservice System",
    version="1.0.0"
)

# Enable CORS for local React dashboard
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount API v1 router
app.include_router(api_router, prefix="/api/v1")

@app.get("/")
async def root():
    """Root health check endpoint."""
    return {
        "status": "online",
        "service": "EasyMail Zero Trust Backend Engine",
        "version": "1.0.0",
        "documentation_url": "http://127.0.0.1:8000/docs"
    }