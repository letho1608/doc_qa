"""
FastAPI Main Application
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from contextlib import asynccontextmanager
from pathlib import Path

from app.core.config import settings
from app.core.logging import logger
from app.api import documents, chat, conversations
from app.services.rag_service import get_rag_service
from app.services.conversation_service import ConversationService
from app.models.query import HealthResponse


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifecycle manager"""
    # Startup
    logger.info("Đang khởi động RAG System...")
    get_rag_service()  # Initialize RAG service
    logger.info("RAG System đã sẵn sàng!")
    
    yield
    
    # Shutdown
    logger.info("Đang tắt RAG System...")


# Create FastAPI app
app = FastAPI(
    title=settings.app_name,
    description="Hệ thống Retrieval-Augmented Generation với LangChain, FAISS và Gemini",
    version=settings.app_version,
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # TODO: Restrict in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files (frontend)
frontend_dir = Path(__file__).parent.parent / "frontend"
if frontend_dir.exists():
    app.mount("/assets", StaticFiles(directory=str(frontend_dir / "assets")), name="assets")

# Include API routers
app.include_router(documents.router, prefix="/api/documents", tags=["Documents"])
app.include_router(chat.router, prefix="/api/chat", tags=["Chat"])
app.include_router(conversations.router, prefix="/api/conversations", tags=["Conversations"])


@app.get("/", response_class=FileResponse)
async def root():
    """Serve frontend"""
    index_file = frontend_dir / "index.html"
    if index_file.exists():
        return FileResponse(index_file)
    return {"message": "RAG System API", "docs": "/docs"}


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    rag = get_rag_service()
    docs_count = len(rag.list_documents())
    conversations_count = len(ConversationService.list_conversations())
    
    return HealthResponse(
        status="healthy",
        version=settings.app_version,
        documents_count=docs_count,
        conversations_count=conversations_count,
        vector_store_ready=rag.vector_store is not None
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="localhost",
        port=8000,
        reload=settings.debug
    )
