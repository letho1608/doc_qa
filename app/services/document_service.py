"""
Document Service - Document management logic
"""
from pathlib import Path
from typing import List, Optional
import uuid
import logging
import aiofiles

from fastapi import UploadFile

from app.core.config import settings
from app.models.document import DocumentMetadata, DocumentResponse, FileType
from app.services.rag_service import get_rag_service
from app.utils.file_handler import FileHandler

logger = logging.getLogger(__name__)


class DocumentService:
    """Service for document management"""
    
    @staticmethod
    async def upload_document(file: UploadFile) -> DocumentResponse:
        """
        Upload và xử lý document
        
        Args:
            file: Uploaded file
            
        Returns:
            DocumentResponse
            
        Raises:
            ValueError: If file type not supported or file too large
        """
        # Validate file extension
        if not FileHandler.is_supported(file.filename):
            raise ValueError(
                f"Định dạng file không được hỗ trợ. "
                f"Chỉ hỗ trợ: {', '.join(settings.allowed_extensions)}"
            )
        
        # Read file content
        content = await file.read()
        file_size = len(content)
        
        # Validate file size
        if not FileHandler.validate_file_size(file_size, settings.max_file_size):
            max_size_mb = settings.max_file_size / (1024 * 1024)
            raise ValueError(f"File quá lớn. Kích thước tối đa: {max_size_mb}MB")
        
        # Generate unique ID
        doc_id = str(uuid.uuid4())
        
        # Save file
        file_type = FileHandler.get_file_type(file.filename)
        file_path = settings.uploads_dir / f"{doc_id}_{file.filename}"
        
        async with aiofiles.open(file_path, 'wb') as f:
            await f.write(content)
        
        logger.info(f"Đã lưu file: {file.filename} ({FileHandler.format_file_size(file_size)})")
        
        # Create metadata
        metadata = DocumentMetadata(
            doc_id=doc_id,
            filename=file.filename,
            file_type=file_type,
            file_size=file_size,
            chunks_count=0,  # Will be updated by RAG service
            file_path=str(file_path)
        )
        
        # Add to RAG system
        rag_service = get_rag_service()
        result = rag_service.add_document(file_path, doc_id, metadata)
        
        # Update chunks count
        metadata.chunks_count = result['chunks_count']
        metadata.pages_count = result['pages_count']
        
        return DocumentResponse(**metadata.dict())
    
    @staticmethod
    def get_documents() -> List[DocumentResponse]:
        """
        Lấy danh sách tất cả documents
        
        Returns:
            List of DocumentResponse
        """
        rag_service = get_rag_service()
        documents = rag_service.list_documents()
        return [DocumentResponse(**doc.dict()) for doc in documents]
    
    @staticmethod
    def get_document(doc_id: str) -> Optional[DocumentResponse]:
        """
        Lấy thông tin một document
        
        Args:
            doc_id: Document ID
            
        Returns:
            DocumentResponse or None
        """
        rag_service = get_rag_service()
        metadata = rag_service.documents_metadata.get(doc_id)
        if metadata:
            return DocumentResponse(**metadata.dict())
        return None
    
    @staticmethod
    def delete_document(doc_id: str) -> bool:
        """
        Xóa document
        
        Args:
            doc_id: Document ID
            
        Returns:
            True if successful
        """
        rag_service = get_rag_service()
        
        # Get metadata to find file path
        metadata = rag_service.documents_metadata.get(doc_id)
        if not metadata:
            return False
        
        # Delete physical file
        file_path = Path(metadata.file_path)
        if file_path.exists():
            file_path.unlink()
            logger.info(f"Đã xóa file: {file_path.name}")
        
        # Delete from RAG system
        return rag_service.delete_document(doc_id)
    
    @staticmethod
    def search_documents(query: str, k: int = 10) -> List[dict]:
        """
        Search trong documents
        
        Args:
            query: Search query
            k: Number of results
            
        Returns:
            List of search results
        """
        rag_service = get_rag_service()
        return rag_service.search_documents(query, k)
