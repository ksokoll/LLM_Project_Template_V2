# pipeline.py
from validator import Validator
from processor import Processor
from models import PipelineResult
import logging
import time

logger = logging.getLogger(__name__)

class Pipeline:
    """
    Simplified pipeline orchestration.
    
    Architecture:
    - 3 components: Validator → Processor → ResultFormatter
    - Each component owns its errors (raises RuntimeError)
    - Pipeline propagates exceptions to FastAPI
    - No try/except (clean separation of concerns)
    """
    
    def __init__(self):
        logger.info("Initializing pipeline components...")
        
        self.validator = Validator()
        logger.info("✓ Validator ready")
        
        self.processor = Processor()
        logger.info("✓ Processor ready")
        
        self.process_step = "0_pipeline"
        
        logger.info("✅ Pipeline initialized successfully")
    
    def process(self, query: str) -> PipelineResult:
        """
        Process query through complete pipeline.
        
        Steps:
        1. Validate query (generate ID, check length)
        2. Process with LLM (optional RAG)
        3. Format results
        
        Args:
            query: Raw user query string
            
        Returns:
            PipelineResult with answer and metadata
            
        Raises:
            RuntimeError: If any step fails (propagated from components)
        """
        
        start_time = time.time()
        
        # Step 1: Validate
        validated_query = self.validator.validate(query)
        
        logger.info(
            "Pipeline started",
            extra={
                "process_step": self.process_step,
                "query_id": validated_query.query_id
            }
        )
        
        # Step 2: Process with LLM
        processor_result = self.processor.process(validated_query)
        
         # Step 3: Format results
        processing_time_ms = (time.time() - start_time) * 1000
        
        final_result = PipelineResult(
            query_id=processor_result.query_id,
            query=validated_query.query,
            answer=processor_result.answer,
            sources=processor_result.sources_used,
            processing_time_ms=processing_time_ms,
            metadata={
                "sources_count": len(processor_result.sources_used),
                "has_context": len(processor_result.sources_used) > 0
            }
        )
        
        logger.info(
            "Pipeline completed",
            extra={
                "process_step": self.process_step,
                "query_id": validated_query.query_id,
                "processing_time_ms": round(processing_time_ms, 2)
            }
        )
        
        return final_result
