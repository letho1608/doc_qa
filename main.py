import uvicorn
import warnings
import logging
import os

# Suppress warnings
warnings.filterwarnings("ignore", category=FutureWarning)
warnings.filterwarnings("ignore", category=UserWarning)
# Suppress specific pynvml warning
os.environ["PYTORCH_CUDA_ALLOC_CONF"] = "expandable_segments:True"

from app.core.config import settings

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%H:%M:%S'
)
# Tắt log của một số thư viện ồn ào
logging.getLogger("httpx").setLevel(logging.WARNING)
logging.getLogger("httpcore").setLevel(logging.WARNING)
logging.getLogger("google").setLevel(logging.WARNING)

if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host="localhost",
        port=8000,
        reload=settings.debug
    )
