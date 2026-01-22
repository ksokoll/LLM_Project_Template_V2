# config.py
from pydantic import Field
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    """Configuration settings for the pipeline"""
    
    # ==================== API Keys ====================
    openai_api_key: str | None = Field(default=None, env="OPENAI_API_KEY")
    
    # ==================== Model Settings ====================
    model_name: str = "gpt-4o-mini"
    temperature: float = 0.7
    max_tokens: int = 1000
    
    # ==================== Validation Settings ====================
    min_query_length: int = 3
    max_query_length: int = 2000
    
    # ==================== Retrieval Settings (Optional) ====================
    enable_retrieval: bool = False  # Toggle RAG on/off
    knowledge_base_path: str = "data/faq.jsonl"
    top_k: int = 3  # Number of documents to retrieve
    
    # ==================== Processing Settings ====================
    processing_mode: str = "default"  # Future: "fast", "accurate", etc.
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False
        env_file_required = False  # Works both local (.env) and cloud (system vars)

# Global settings instance
settings = Settings()
