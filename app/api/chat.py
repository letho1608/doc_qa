"""
Chat API Routes
"""
from fastapi import APIRouter, HTTPException
from typing import Optional
import logging

from app.models.query import QueryRequest, QueryResponse
from app.services.rag_service import get_rag_service
from app.services.conversation_service import ConversationService

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/query", response_model=QueryResponse)
async def query_rag(request: QueryRequest):
    """
    Query RAG system
    
    - **question**: Câu hỏi cần trả lời
    - **conversation_id**: ID của conversation (optional)
    - **k**: Số lượng documents liên quan (default: 5)
    """
    try:
        # Get RAG service
        rag_service = get_rag_service()
        
        # Query
        response = await rag_service.query(request.question, request.k)
        
        # Save to conversation if provided
        if request.conversation_id:
            # Add user message
            ConversationService.add_message(
                request.conversation_id,
                "user",
                request.question
            )
            
            # Add assistant message
            source_filenames = [src.filename for src in response.sources]
            ConversationService.add_message(
                request.conversation_id,
                "assistant",
                response.answer,
                source_filenames
            )
            
            response.conversation_id = request.conversation_id
        
        return response
        
    except Exception as e:
        logger.error(f"Query error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Lỗi khi query: {str(e)}")
