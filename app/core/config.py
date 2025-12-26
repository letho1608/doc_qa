"""
Core configuration for RAG System
"""
from pydantic_settings import BaseSettings
from pathlib import Path


class Settings(BaseSettings):
    """Application settings"""
    
    # API Keys
    google_api_key: str = ""
    
    # App Info
    app_name: str = "DocQA"
    app_version: str = "2.0.0"
    debug: bool = False
    
    # Paths
    base_dir: Path = Path(__file__).parent.parent.parent
    storage_dir: Path = base_dir / "storage"
    uploads_dir: Path = storage_dir / "uploads"
    vector_store_dir: Path = storage_dir / "vector_store"
    conversations_dir: Path = storage_dir / "conversations"
    
    # RAG Settings
    chunk_size: int = 500
    chunk_overlap: int = 50
    retrieval_k: int = 5
    
    # Embedding Settings
    embedding_type: str = "sentence-transformers"  # "sentence-transformers" hoặc "google"
    sentence_transformer_model: str = "paraphrase-multilingual-MiniLM-L12-v2"
    embedding_device: str = "cpu"  # "cpu" hoặc "cuda"
    
    # LLM Settings
    use_llm: bool = True  # Có sử dụng LLM để generate answer không
    llm_type: str = "google"  # "google" hoặc "none"
    llm_model: str = "gemini-2.5-flash"  # Hoặc "gemini-pro"
    llm_temperature: float = 0.7
    embedding_model: str = "models/embedding-001"  # Chỉ dùng khi embedding_type="google"
    
    # File Upload
    max_file_size: int = 10 * 1024 * 1024  # 10MB
    allowed_extensions: list = [".txt", ".pdf", ".md", ".docx", ".doc"]
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


# Global settings instance
settings = Settings()

# Ensure directories exist
settings.storage_dir.mkdir(exist_ok=True)
settings.uploads_dir.mkdir(exist_ok=True)
settings.vector_store_dir.mkdir(exist_ok=True)
settings.conversations_dir.mkdir(exist_ok=True)
