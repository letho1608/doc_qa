"""
Conversations API Routes
"""
from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import PlainTextResponse
from typing import Optional
import logging

from app.models.conversation import (
    Conversation,
    ConversationCreate,
    ConversationMetadata,
    ConversationListResponse
)
from app.services.conversation_service import ConversationService

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("", response_model=Conversation)
async def create_conversation(data: ConversationCreate):
    """Tạo conversation mới"""
    try:
        conversation = ConversationService.create_conversation(data.title)
        return conversation
    except Exception as e:
        logger.error(f"Create conversation error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("", response_model=ConversationListResponse)
async def list_conversations():
    """Lấy danh sách tất cả conversations"""
    try:
        conversations = ConversationService.list_conversations()
        return ConversationListResponse(
            conversations=conversations,
            total=len(conversations)
        )
    except Exception as e:
        logger.error(f"List conversations error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{conversation_id}", response_model=Conversation)
async def get_conversation(conversation_id: str):
    """Lấy conversation theo ID"""
    conversation = ConversationService.get_conversation(conversation_id)
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation không tồn tại")
    return conversation


@router.delete("/{conversation_id}")
async def delete_conversation(conversation_id: str):
    """Xóa conversation"""
    try:
        success = ConversationService.delete_conversation(conversation_id)
        if not success:
            raise HTTPException(status_code=404, detail="Conversation không tồn tại")
        return {"success": True, "message": "Đã xóa conversation thành công"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Delete conversation error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{conversation_id}/export")
async def export_conversation(
    conversation_id: str,
    format: str = Query("json", regex="^(json|markdown)$")
):
    """
    Export conversation
    
    - **format**: Export format (json hoặc markdown)
    """
    try:
        exported = ConversationService.export_conversation(conversation_id, format)
        
        if not exported:
            raise HTTPException(status_code=404, detail="Conversation không tồn tại")
        
        if format == "markdown":
            return PlainTextResponse(content=exported, media_type="text/markdown")
        else:
            return PlainTextResponse(content=exported, media_type="application/json")
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Export error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
