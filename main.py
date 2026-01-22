# main.py
from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from pipeline import Pipeline
import logging

# ==================== Logging Setup ====================

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

# ==================== FastAPI App ====================

app = FastAPI(
    title="AI Pipeline API",
    description="Simplified LLM pipeline with optional RAG",
    version="2.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Production: Specify allowed origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ==================== Request/Response Models ====================

class QueryRequest(BaseModel):
    """API request schema"""
    query: str
    
    class Config:
        json_schema_extra = {
            "example": {
                "query": "How do I reset my password?"
            }
        }

# ==================== Dependency Injection ====================

def get_pipeline() -> Pipeline:
    """
    Dependency injection for pipeline.
    Creates singleton pipeline instance.
    """
    if not hasattr(get_pipeline, "instance"):
        get_pipeline.instance = Pipeline()
    return get_pipeline.instance

# ==================== API Endpoints ====================

@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "message": "AI Pipeline API",
        "status": "running",
        "version": "2.0.0"
    }

@app.get("/health")
async def health_check():
    """Detailed health check"""
    return {
        "status": "healthy",
        "message": "Pipeline ready"
    }

@app.post("/process")
async def process_query(
    request: QueryRequest,
    pipeline: Pipeline = Depends(get_pipeline)
):
    """
    Process user query through pipeline.
    
    Automatic error handling:
    - Pydantic validation errors → HTTP 422
    - RuntimeError from pipeline → HTTP 500
    
    No manual try/except needed - FastAPI handles it.
    """
    
    logger.info(f"Received query: {request.query[:50]}...")
    
    # Process through pipeline
    # Exceptions automatically converted to HTTP responses by FastAPI
    result = pipeline.process(request.query)
    
    return result

# ==================== Startup Event ====================

@app.on_event("startup")
async def startup_event():
    """Initialize pipeline on startup"""
    logger.info("="*50)
    logger.info("🚀 API Server Starting...")
    logger.info("="*50)
    
    # Pre-initialize pipeline
    get_pipeline()
    
    logger.info("✅ Server ready")
