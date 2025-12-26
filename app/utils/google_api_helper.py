"""
Utility để cấu hình HTTP transport cho Google API
"""
import os
import logging
from typing import Optional

logger = logging.getLogger(__name__)


def configure_google_api_transport():
    """
    Cấu hình HTTP transport cho Google API để xử lý vấn đề kết nối
    """
    # Thiết lập biến môi trường để tăng timeout cho gRPC
    os.environ.setdefault('GRPC_ENABLE_FORK_SUPPORT', '1')
    os.environ.setdefault('GRPC_POLL_STRATEGY', 'poll')
    
    # Tăng timeout cho DNS resolution
    os.environ.setdefault('GRPC_DNS_RESOLVER', 'native')
    
    # Disable IPv6 nếu có vấn đề
    # os.environ.setdefault('GRPC_ENABLE_IPV6', '0')
    
    # Cấu hình SSL/TLS
    # CẢNH BÁO: Chỉ bật nếu thực sự cần thiết để debug
    # os.environ.setdefault('GRPC_SSL_CIPHER_SUITES', 'HIGH')
    
    # Tăng verbosity cho debug (uncomment nếu cần)
    # os.environ.setdefault('GRPC_VERBOSITY', 'DEBUG')
    # os.environ.setdefault('GRPC_TRACE', 'all')
    
    logger.info("Đã cấu hình Google API transport settings")


def test_google_api_connection(api_key: str) -> bool:
    """
    Test kết nối đến Google API
    
    Args:
        api_key: Google API key
        
    Returns:
        True nếu kết nối thành công
    """
    try:
        from langchain_google_genai import GoogleGenerativeAIEmbeddings
        
        logger.info("Đang test kết nối đến Google API...")
        
        # Tạo embeddings instance với timeout ngắn để test
        embeddings = GoogleGenerativeAIEmbeddings(
            model="models/embedding-001",
            google_api_key=api_key,
            request_timeout=30,
            max_retries=2
        )
        
        # Test với một text đơn giản
        test_text = "Hello, this is a test."
        result = embeddings.embed_query(test_text)
        
        if result and len(result) > 0:
            logger.info("✓ Kết nối đến Google API thành công!")
            return True
        else:
            logger.warning("✗ Kết nối thành công nhưng không nhận được kết quả")
            return False
            
    except Exception as e:
        logger.error(f"✗ Lỗi khi test kết nối: {str(e)}")
        logger.error("Vui lòng kiểm tra:")
        logger.error("  1. API key có hợp lệ không")
        logger.error("  2. Firewall/Antivirus có chặn kết nối không")
        logger.error("  3. Kết nối internet có ổn định không")
        return False
