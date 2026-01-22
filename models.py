# models.py
from pydantic import BaseModel, Field, field_validator

# ==================== Input Models ====================

class UserQuery(BaseModel):
    """User query with generated ID"""
    query_id: str
    query: str
    
    @field_validator('query')
    def validate_query(cls, v):
        """Validate query is not empty"""
        if not v or not v.strip():
            raise ValueError('Query cannot be empty')
        return v.strip()


# ==================== Processor Models ====================

class ProcessorResult(BaseModel):
    """Result from processor (LLM output)"""
    query_id: str
    answer: str
    sources_used: list[str] = []  # Retrieved documents (if RAG enabled)
    confidence: float = 0.0  # Optional: LLM confidence score


# ==================== Pipeline Output ====================

class PipelineResult(BaseModel):
    """Complete pipeline response"""
    query_id: str
    query: str
    answer: str
    sources: list[str] = []
    processing_time_ms: float = 0.0
    metadata: dict = {}
