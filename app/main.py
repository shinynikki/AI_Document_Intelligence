from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse

from app.core.database import Base, engine
from app.routes.documents import router as documents_router


# =========================================================
# DATABASE INITIALIZATION
# =========================================================

Base.metadata.create_all(bind=engine)


# =========================================================
# FASTAPI APPLICATION
# =========================================================

app = FastAPI(
    title="Intelligent Document Extraction API",
    description=(
        "AI-powered document extraction, validation and "
        "persistence platform."
    ),
    version="1.0.0",
)


# =========================================================
# CORS CONFIGURATION
# =========================================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://ai-document-intelligence-frontend-cye5.onrender.com",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# =========================================================
# ROUTERS
# =========================================================

app.include_router(documents_router)


# =========================================================
# HEALTH CHECK
# =========================================================

@app.get("/api/v1/health", tags=["Health"])
def health_check():
    return {
        "status": "healthy",
        "service": "Intelligent Document Extraction API",
    }


@app.get("/api/v1", tags=["Health"])
def api_root():
    return {
        "message": "Intelligent Document Extraction API",
        "docs": "/docs",
        "health": "/api/v1/health",
    }


# =========================================================
# FRONTEND SERVING
# =========================================================

frontend_path = Path(__file__).resolve().parent.parent / "frontend"


@app.get("/", include_in_schema=False)
def serve_frontend():
    return FileResponse(frontend_path / "index.html")