"""
Pydantic models for documents
"""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from enum import Enum


class FileType(str, Enum):
    """Supported file types"""
    TXT = "txt"
    PDF = "pdf"
    MD = "md"
    DOCX = "docx"
    DOC = "doc"


class DocumentCreate(BaseModel):
    """Schema for creating a document"""
    filename: str
    file_type: str
    file_size: int


class DocumentChunk(BaseModel):
    """Schema for document chunk"""
    content: str
    doc_id: str
    filename: str
    chunk_index: int


class DocumentMetadata(BaseModel):
    """Schema for document metadata"""
    doc_id: str
    filename: str
    file_type: str
    file_size: int
    chunks_count: int
    pages_count: int = 0
    created_at: datetime = Field(default_factory=datetime.now)
    file_path: str


class DocumentResponse(BaseModel):
    """Schema for document response"""
    doc_id: str
    filename: str
    file_type: str
    file_size: int
    chunks_count: int
    pages_count: int
    created_at: datetime
    
    class Config:
        from_attributes = True


class DocumentListResponse(BaseModel):
    """Schema for document list response"""
    documents: List[DocumentResponse]
    total: int


class DocumentSearchResult(BaseModel):
    """Schema for document search result"""
    doc_id: str
    filename: str
    content: str
    score: float
