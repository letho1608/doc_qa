"""
Documents API Routes
"""
from fastapi import APIRouter, UploadFile, File, HTTPException, Query
from typing import List

from app.models.document import DocumentResponse, DocumentListResponse
from app.services.document_service import DocumentService
import logging

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/upload", response_model=DocumentResponse)
async def upload_document(file: UploadFile = File(...)):
    """
    Upload một document
    
    - **file**: Document file (TXT, PDF, MD, DOCX, DOC)
    """
    try:
        return await DocumentService.upload_document(file)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Upload error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Lỗi khi upload: {str(e)}")


@router.get("", response_model=DocumentListResponse)
async def get_documents():
    """Lấy danh sách tất cả documents"""
    try:
        documents = DocumentService.get_documents()
        return DocumentListResponse(
            documents=documents,
            total=len(documents)
        )
    except Exception as e:
        logger.error(f"Get documents error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{doc_id}", response_model=DocumentResponse)
async def get_document(doc_id: str):
    """Lấy thông tin một document"""
    document = DocumentService.get_document(doc_id)
    if not document:
        raise HTTPException(status_code=404, detail="Document không tồn tại")
    return document


@router.delete("/{doc_id}")
async def delete_document(doc_id: str):
    """Xóa document"""
    try:
        success = DocumentService.delete_document(doc_id)
        if not success:
            raise HTTPException(status_code=404, detail="Document không tồn tại")
        return {"success": True, "message": "Đã xóa document thành công"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Delete error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/search/")
async def search_documents(
    q: str = Query(..., description="Search query"),
    k: int = Query(10, ge=1, le=50, description="Number of results")
):
    """Search trong documents"""
    try:
        results = DocumentService.search_documents(q, k)
        return {"results": results, "total": len(results)}
    except Exception as e:
        logger.error(f"Search error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
