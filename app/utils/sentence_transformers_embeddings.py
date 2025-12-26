"""
Sentence Transformers Embeddings Wrapper cho Langchain
Cho phép sử dụng Sentence Transformers models với Langchain
"""
from typing import List
import logging
from langchain_core.embeddings import Embeddings

logger = logging.getLogger(__name__)


class SentenceTransformerEmbeddings(Embeddings):
    """
    Wrapper class để sử dụng Sentence Transformers với Langchain
    
    Hỗ trợ:
    - Chạy offline (không cần internet sau khi download model)
    - Đa ngôn ngữ (tiếng Việt)
    - CPU và GPU
    """
    
    def __init__(
        self,
        model_name: str = "paraphrase-multilingual-MiniLM-L12-v2",
        device: str = "cpu",
        cache_folder: str = None
    ):
        """
        Khởi tạo Sentence Transformer Embeddings
        
        Args:
            model_name: Tên model từ Sentence Transformers
            device: 'cpu' hoặc 'cuda'
            cache_folder: Thư mục cache model (optional)
        """
        try:
            from sentence_transformers import SentenceTransformer
            
            logger.info(f"Đang load Sentence Transformer model: {model_name}")
            logger.info(f"Device: {device}")
            
            self.model = SentenceTransformer(
                model_name,
                device=device,
                cache_folder=cache_folder
            )
            
            self.model_name = model_name
            self.device = device
            
            logger.info(f"✓ Đã load model thành công: {model_name}")
            logger.info(f"✓ Embedding dimension: {self.model.get_sentence_embedding_dimension()}")
            
        except ImportError:
            raise ImportError(
                "sentence-transformers chưa được cài đặt. "
                "Vui lòng cài đặt: pip install sentence-transformers"
            )
        except Exception as e:
            logger.error(f"Lỗi khi load model: {str(e)}")
            raise
    
    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """
        Embed một list các documents
        
        Args:
            texts: List các text cần embed
            
        Returns:
            List các embedding vectors
        """
        try:
            logger.debug(f"Đang embed {len(texts)} documents...")
            
            # Encode texts thành embeddings
            embeddings = self.model.encode(
                texts,
                convert_to_numpy=True,
                show_progress_bar=False,
                batch_size=32
            )
            
            # Convert numpy array thành list
            embeddings_list = embeddings.tolist()
            
            logger.debug(f"✓ Đã embed {len(texts)} documents")
            return embeddings_list
            
        except Exception as e:
            logger.error(f"Lỗi khi embed documents: {str(e)}")
            raise
    
    def embed_query(self, text: str) -> List[float]:
        """
        Embed một query text
        
        Args:
            text: Text cần embed
            
        Returns:
            Embedding vector
        """
        try:
            logger.debug(f"Đang embed query: {text[:50]}...")
            
            # Encode text thành embedding
            embedding = self.model.encode(
                text,
                convert_to_numpy=True,
                show_progress_bar=False
            )
            
            # Convert numpy array thành list
            embedding_list = embedding.tolist()
            
            logger.debug("✓ Đã embed query")
            return embedding_list
            
        except Exception as e:
            logger.error(f"Lỗi khi embed query: {str(e)}")
            raise
    
    def get_embedding_dimension(self) -> int:
        """Lấy dimension của embedding vector"""
        return self.model.get_sentence_embedding_dimension()
