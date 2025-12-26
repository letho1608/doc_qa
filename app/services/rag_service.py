"""
RAG Service - Core RAG logic with FAISS and embeddings
"""
from pathlib import Path
from typing import List, Dict, Any, Optional
import pickle
import logging

from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain.schema import Document

from app.core.config import settings
from app.utils.file_handler import FileHandler
from app.utils.sentence_transformers_embeddings import SentenceTransformerEmbeddings
from app.models.document import DocumentMetadata
from app.models.query import QueryResponse, SourceDocument

logger = logging.getLogger(__name__)


class RAGService:
    """Hệ thống RAG với FAISS vector store và embeddings (Sentence Transformers hoặc Google Gemini)"""
    
    _instance = None
    
    def __new__(cls):
        """Singleton pattern"""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        """Khởi tạo RAG service"""
        if self._initialized:
            return
        
        logger.info(f"Đang khởi tạo RAG Service với embedding type: {settings.embedding_type}")
        
        # Khởi tạo Embeddings dựa trên cấu hình
        if settings.embedding_type == "sentence-transformers":
            logger.info("Sử dụng Sentence Transformers cho embeddings (offline)")
            self.embeddings = SentenceTransformerEmbeddings(
                model_name=settings.sentence_transformer_model,
                device=settings.embedding_device
            )
            logger.info("✓ Embeddings đã sẵn sàng (offline)")
            
        elif settings.embedding_type == "google":
            logger.info("Sử dụng Google Gemini cho embeddings")
            
            # Import động
            from langchain_google_genai import GoogleGenerativeAIEmbeddings
            from app.utils.google_api_helper import configure_google_api_transport
            
            # Check API key
            if not settings.google_api_key:
                raise ValueError(
                    "GOOGLE_API_KEY is required when using Google embeddings. "
                    "Please add your API key to .env"
                )
            
            # Cấu hình transport
            configure_google_api_transport()
            
            self.embeddings = GoogleGenerativeAIEmbeddings(
                model=settings.embedding_model,
                google_api_key=settings.google_api_key,
                request_timeout=180,
                max_retries=5
            )
            logger.info("✓ Google Gemini Embeddings đã sẵn sàng")
        else:
            raise ValueError(f"Embedding type không hợp lệ: {settings.embedding_type}")
        
        # Khởi tạo LLM (tách biệt với embeddings)
        if settings.use_llm and settings.llm_type == "google":
            logger.info("Đang khởi tạo Google Gemini LLM...")
            
            # Import động
            from langchain_google_genai import ChatGoogleGenerativeAI
            from app.utils.google_api_helper import configure_google_api_transport
            
            # Check API key
            if not settings.google_api_key:
                raise ValueError(
                    "GOOGLE_API_KEY is required when using Google LLM. "
                    "Please add your API key to .env"
                )
            
            # Cấu hình transport (nếu chưa)
            configure_google_api_transport()
            
            self.llm = ChatGoogleGenerativeAI(
                model=settings.llm_model,
                google_api_key=settings.google_api_key,
                temperature=settings.llm_temperature,
                request_timeout=180,
                max_retries=5
            )
            logger.info("✓ Google Gemini LLM đã sẵn sàng")
        else:
            self.llm = None
            logger.info("Chạy ở chế độ không có LLM (chỉ trả về context)")
        
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=settings.chunk_size,
            chunk_overlap=settings.chunk_overlap,
            length_function=len,
        )
        
        self.vector_store: Optional[FAISS] = None
        self.documents_metadata: Dict[str, DocumentMetadata] = {}
        
        # Paths
        self.vector_store_file = settings.vector_store_dir / "faiss_index"
        self.metadata_file = settings.vector_store_dir / "documents_metadata.pkl"
        
        # Load existing data
        self._load_vector_store()
        self._initialized = True
        logger.info("RAG Service đã được khởi tạo thành công")
    
    def _load_vector_store(self):
        """Load vector store từ disk nếu có"""
        try:
            if self.vector_store_file.exists():
                self.vector_store = FAISS.load_local(
                    str(self.vector_store_file),
                    self.embeddings,
                    allow_dangerous_deserialization=True
                )
                logger.info("Đã load vector store từ disk")
                
                # Load metadata
                if self.metadata_file.exists():
                    with open(self.metadata_file, 'rb') as f:
                        self.documents_metadata = pickle.load(f)
                    logger.info(f"Đã load metadata của {len(self.documents_metadata)} documents")
            else:
                logger.info("Chưa có vector store, sẽ tạo mới khi add documents")
        except Exception as e:
            logger.error(f"Lỗi khi load vector store: {str(e)}")
            self.vector_store = None
            self.documents_metadata = {}
    
    def _save_vector_store(self):
        """Lưu vector store vào disk"""
        try:
            if self.vector_store:
                self.vector_store.save_local(str(self.vector_store_file))
                logger.info("Đã lưu vector store vào disk")
                
                # Lưu metadata
                with open(self.metadata_file, 'wb') as f:
                    pickle.dump(self.documents_metadata, f)
                logger.info("Đã lưu documents metadata")
        except Exception as e:
            logger.error(f"Lỗi khi lưu vector store: {str(e)}")
            raise
    
    def add_document(self, file_path: Path, doc_id: str, metadata: DocumentMetadata) -> Dict[str, Any]:
        """
        Thêm document vào vector store
        
        Args:
            file_path: Path to document file
            doc_id: Unique document ID
            metadata: Document metadata
            
        Returns:
            Dict with document info
        """
        try:
            logger.info(f"Đang xử lý document: {file_path.name}")
            
            # Load document using FileHandler
            documents = FileHandler.load_document(file_path)
            
            # Thêm metadata
            for doc in documents:
                doc.metadata.update({
                    'doc_id': doc_id,
                    'filename': file_path.name,
                    'source': str(file_path)
                })
            
            # Split thành chunks
            chunks = self.text_splitter.split_documents(documents)
            logger.info(f"Đã chia thành {len(chunks)} chunks")
            
            # Thêm vào vector store
            if self.vector_store is None:
                self.vector_store = FAISS.from_documents(chunks, self.embeddings)
                logger.info("Đã tạo vector store mới")
            else:
                self.vector_store.add_documents(chunks)
                logger.info("Đã thêm vào vector store hiện có")
            
            # Lưu metadata
            self.documents_metadata[doc_id] = metadata
            
            # Lưu vào disk
            self._save_vector_store()
            
            return {
                'doc_id': doc_id,
                'filename': file_path.name,
                'chunks_count': len(chunks),
                'pages_count': len(documents)
            }
            
        except Exception as e:
            logger.error(f"Lỗi khi add document: {str(e)}")
            raise
    
    def delete_document(self, doc_id: str) -> bool:
        """
        Xóa document khỏi vector store
        
        Args:
            doc_id: Document ID to delete
            
        Returns:
            True if successful
        """
        try:
            if doc_id not in self.documents_metadata:
                logger.warning(f"Document {doc_id} không tồn tại")
                return False
            
            # Xóa metadata
            del self.documents_metadata[doc_id]
            
            # Rebuild vector store
            if self.documents_metadata:
                self._rebuild_vector_store()
            else:
                # Nếu không còn document nào, xóa vector store
                self.vector_store = None
                if self.vector_store_file.exists():
                    import shutil
                    shutil.rmtree(settings.vector_store_dir)
                    settings.vector_store_dir.mkdir(exist_ok=True)
                logger.info("Đã xóa vector store (không còn documents)")
            
            return True
            
        except Exception as e:
            logger.error(f"Lỗi khi xóa document: {str(e)}")
            raise
    
    def _rebuild_vector_store(self):
        """Rebuild vector store từ các documents còn lại"""
        try:
            logger.info("Đang rebuild vector store...")
            all_chunks = []
            
            for doc_id, metadata in self.documents_metadata.items():
                file_path = Path(metadata.file_path)
                if file_path.exists():
                    documents = FileHandler.load_document(file_path)
                    
                    # Thêm metadata
                    for doc in documents:
                        doc.metadata.update({
                            'doc_id': doc_id,
                            'filename': file_path.name,
                            'source': str(file_path)
                        })
                    
                    chunks = self.text_splitter.split_documents(documents)
                    all_chunks.extend(chunks)
            
            # Tạo vector store mới
            if all_chunks:
                self.vector_store = FAISS.from_documents(all_chunks, self.embeddings)
                self._save_vector_store()
                logger.info(f"Đã rebuild vector store với {len(all_chunks)} chunks")
            
        except Exception as e:
            logger.error(f"Lỗi khi rebuild vector store: {str(e)}")
            raise
    
    def list_documents(self) -> List[DocumentMetadata]:
        """Lấy danh sách tất cả documents"""
        return list(self.documents_metadata.values())
    
    async def query(self, question: str, k: int = None) -> QueryResponse:
        """
        Query RAG system
        
        Args:
            question: User question
            k: Number of documents to retrieve
            
        Returns:
            QueryResponse with answer and sources
        """
        try:
            if self.vector_store is None:
                return QueryResponse(
                    answer='Chưa có document nào được upload. Vui lòng upload documents trước.',
                    sources=[]
                )
            
            k = k or settings.retrieval_k
            logger.info(f"Query: {question}")
            
            # Retrieve relevant documents
            retriever = self.vector_store.as_retriever(
                search_type="similarity",
                search_kwargs={"k": k}
            )
            retrieved_docs = retriever.invoke(question)
            
            # Chuẩn bị context
            context = "\n\n".join([doc.page_content for doc in retrieved_docs])
            
            # Generate answer
            if self.llm is not None:
                # Có LLM - Generate answer với AI
                prompt = f"""Dựa trên thông tin sau đây, hãy trả lời câu hỏi một cách chính xác và chi tiết.

Thông tin tham khảo:
{context}

Câu hỏi: {question}

Trả lời:"""
                
                response = self.llm.invoke(prompt)
                answer = response.content.strip()
            else:
                # Không có LLM - Trả về context trực tiếp
                answer = f"""**Thông tin liên quan từ documents:**

{context}

---
*Lưu ý: Hệ thống đang chạy ở chế độ offline (không có LLM). Thông tin trên là các đoạn văn liên quan nhất từ documents được tìm thấy.*"""
            
            # Chuẩn bị sources
            sources = []
            seen_files = set()
            for doc in retrieved_docs:
                filename = doc.metadata.get('filename', 'Unknown')
                if filename not in seen_files:
                    sources.append(SourceDocument(
                        doc_id=doc.metadata.get('doc_id', ''),
                        filename=filename,
                        content=doc.page_content[:200] + '...'
                    ))
                    seen_files.add(filename)
            
            logger.info(f"Đã tạo response từ {len(sources)} sources")
            
            return QueryResponse(
                answer=answer,
                sources=sources
            )
            
        except Exception as e:
            logger.error(f"Lỗi khi query: {str(e)}")
            raise
    
    def search_documents(self, query: str, k: int = 10) -> List[Dict[str, Any]]:
        """
        Search trong documents
        
        Args:
            query: Search query
            k: Number of results
            
        Returns:
            List of search results
        """
        try:
            if self.vector_store is None:
                return []
            
            # Similarity search
            results = self.vector_store.similarity_search_with_score(query, k=k)
            
            search_results = []
            for doc, score in results:
                search_results.append({
                    'doc_id': doc.metadata.get('doc_id', ''),
                    'filename': doc.metadata.get('filename', 'Unknown'),
                    'content': doc.page_content,
                    'score': float(score)
                })
            
            return search_results
            
        except Exception as e:
            logger.error(f"Lỗi khi search: {str(e)}")
            return []


# Global instance
_rag_service: Optional[RAGService] = None


def get_rag_service() -> RAGService:
    """Get RAG service instance (singleton)"""
    global _rag_service
    if _rag_service is None:
        _rag_service = RAGService()
    return _rag_service
