# validator.py
from models import UserQuery
from config import settings
from ulid import ULID
import logging

logger = logging.getLogger(__name__)

class Validator:
    """Validates and preprocesses user queries"""
    
    def __init__(self):
        self.process_step = "1_validation"
    
    def validate(self, query: str) -> UserQuery:
        """
        Validate user query and generate unique ID.
        
        Args:
            query: Raw user query string
            
        Returns:
            UserQuery with validated query and generated ID
            
        Raises:
            RuntimeError: If validation fails (ULID generation, length checks)
        """
        
        # Generate unique ID (ULID for sortable, timestamped IDs)
        try:
            query_id = str(ULID())
        except Exception as e:
            logger.error(
                "ULID generation failed",
                extra={
                    "process_step": self.process_step
                },
                exc_info=True
            )
            raise RuntimeError("Failed to generate query_id") from e
        
        logger.info(
            "Validation started",
            extra={
                "process_step": self.process_step,
                "query_id": query_id,
                "query_length": len(query)
            }
        )
        
        # Clean query
        query_clean = query.strip()
        
        # Validate minimum length
        if len(query_clean) < settings.min_query_length:
            logger.warning(
                "Query too short",
                extra={
                    "process_step": self.process_step,
                    "query_id": query_id,
                    "length": len(query_clean),
                    "minimum": settings.min_query_length
                }
            )
            raise RuntimeError(
                f"Query too short (minimum {settings.min_query_length} characters)"
            )
        
        # Validate maximum length
        if len(query_clean) > settings.max_query_length:
            logger.warning(
                "Query too long",
                extra={
                    "process_step": self.process_step,
                    "query_id": query_id,
                    "length": len(query_clean),
                    "maximum": settings.max_query_length
                }
            )
            raise RuntimeError(
                f"Query too long (maximum {settings.max_query_length} characters)"
            )
        
        logger.info(
            "Validation completed successfully",
            extra={
                "process_step": self.process_step,
                "query_id": query_id
            }
        )
        
        # Return validated query with ID
        return UserQuery(
            query_id=query_id,
            query=query_clean
        )
