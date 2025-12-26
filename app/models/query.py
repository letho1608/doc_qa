"""
Pydantic models for query and response
"""
from pydantic import BaseModel, Field
from typing import List, Optional


class QueryRequest(BaseModel):
    """Schema for query request"""
    question: str = Field(..., min_length=1, description="Câu hỏi cần trả lời")
    conversation_id: Optional[str] = None
    k: int = Field(default=5, ge=1, le=20, description="Số lượng documents liên quan")


class SourceDocument(BaseModel):
    """Schema for source document"""
    doc_id: str
    filename: str
    content: str
    
    class Config:
        from_attributes = True


class QueryResponse(BaseModel):
    """Schema for query response"""
    answer: str
    sources: List[SourceDocument]
    conversation_id: Optional[str] = None
    
    class Config:
        from_attributes = True


class HealthResponse(BaseModel):
    """Schema for health check response"""
    status: str
    version: str
    documents_count: int
    conversations_count: int
    vector_store_ready: bool
