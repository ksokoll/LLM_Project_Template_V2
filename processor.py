# processor.py
from models import UserQuery, ProcessorResult
from openai import OpenAI
from config import settings
from prompts import SYSTEM_PROMPT, SYSTEM_RAG_PROMPT
import logging
import json

logger = logging.getLogger(__name__)

class Processor:
    """
    Unified processor that handles:
    - Optional retrieval (RAG)
    - LLM API calls
    - Response parsing
    
    Replaces: classifier, retriever, generator, quality_check, answer_judge
    """
    
    def __init__(self):
        self.client = OpenAI(api_key=settings.openai_api_key)
        self.prompt_template = self._load_system_prompt()
        self.process_step = "2_processor"
        
        # Log prompt metadata
        logger.info(
            "Prompt loaded",
            extra={
                "process_step": self.process_step,
                "prompt_name": self.prompt_template.name,
                "prompt_version": self.prompt_template.version,
                "tested_models": self.prompt_template.tested_models
            }
        )
        
        # Check if current model is in tested_models list
        if settings.model_name not in self.prompt_template.tested_models:
            logger.warning(
                "Untested prompt/model combination",
                extra={
                    "process_step": self.process_step,
                    "prompt": self.prompt_template.name,
                    "model": settings.model_name,
                    "tested_models": self.prompt_template.tested_models
                }
            )
        
        # Optional: Load knowledge base if retrieval enabled
        if settings.enable_retrieval:
            self.knowledge_base = self._load_knowledge_base()
            logger.info(
                "Knowledge base loaded",
                extra={
                    "process_step": self.process_step,
                    "documents_count": len(self.knowledge_base)
                }
            )
        else:
            self.knowledge_base = []
            logger.info(
                "Retrieval disabled",
                extra={"process_step": self.process_step}
            )
    
    def _load_system_prompt(self):
        """
        Load system prompt from prompts.py module.
        
        Chooses appropriate prompt based on whether RAG is enabled:
        - RAG enabled: Use SYSTEM_RAG_PROMPT (optimized for context)
        - RAG disabled: Use SYSTEM_PROMPT (general purpose)
        
        Returns:
            PromptTemplate object with prompt text and metadata
        """
        if settings.enable_retrieval:
            prompt = SYSTEM_RAG_PROMPT
            logger.debug(
                "Loaded RAG-optimized prompt",
                extra={
                    "process_step": self.process_step,
                    "prompt_version": prompt.version
                }
            )
        else:
            prompt = SYSTEM_PROMPT
            logger.debug(
                "Loaded standard prompt",
                extra={
                    "process_step": self.process_step,
                    "prompt_version": prompt.version
                }
            )
        
        return prompt
    
    def _load_knowledge_base(self) -> list[dict]:
        """
        Load knowledge base from JSONL file.
        
        Returns:
            List of document dictionaries with 'text' field
        """
        try:
            docs = []
            with open(settings.knowledge_base_path, 'r', encoding='utf-8') as f:
                for line in f:
                    doc = json.loads(line.strip())
                    docs.append(doc)
            return docs
        except FileNotFoundError:
            logger.warning(
                "Knowledge base file not found",
                extra={
                    "process_step": self.process_step,
                    "path": settings.knowledge_base_path
                }
            )
            return []
        except Exception as e:
            logger.error(
                "Failed to load knowledge base",
                extra={"process_step": self.process_step},
                exc_info=True
            )
            return []
    
    def _retrieve_context(self, query: str) -> list[str]:
        """
        Simple keyword-based retrieval.
        
        Enhancement option: Replace with FAISS vector search for semantic similarity.
        
        Args:
            query: User query
            
        Returns:
            List of relevant document texts
        """
        if not settings.enable_retrieval or not self.knowledge_base:
            return []
        
        # Simple keyword matching (can be enhanced with embeddings/FAISS)
        relevant_docs = []
        query_lower = query.lower()
        query_words = set(query_lower.split())
        
        # Score documents by keyword overlap
        scored_docs = []
        for doc in self.knowledge_base:
            doc_text = doc.get('text', '')
            doc_lower = doc_text.lower()
            doc_words = set(doc_lower.split())
            
            # Calculate overlap score
            overlap = len(query_words & doc_words)
            if overlap > 0:
                scored_docs.append((overlap, doc_text))
        
        # Sort by score and take top-k
        scored_docs.sort(reverse=True, key=lambda x: x[0])
        relevant_docs = [doc_text for score, doc_text in scored_docs[:settings.top_k]]
        
        logger.debug(
            "Context retrieved",
            extra={
                "process_step": self.process_step,
                "documents_found": len(relevant_docs),
                "query": query[:50]
            }
        )
        
        return relevant_docs
    
    def process(self, item: UserQuery) -> ProcessorResult:
        """
        Process user query with optional RAG.
        
        Steps:
        1. Retrieve context (if enabled)
        2. Build prompt with context
        3. Call LLM API
        4. Parse and validate response
        
        Args:
            item: Validated user query
            
        Returns:
            ProcessorResult with answer and sources
            
        Raises:
            RuntimeError: If LLM API call or parsing fails
        """
        
        logger.info(
            "Processor started",
            extra={
                "process_step": self.process_step,
                "query_id": item.query_id
            }
        )
        
        # Step 1: Retrieve context (if enabled)
        context_docs = self._retrieve_context(item.query)
        
        # Step 2: Build prompt with optional context
        if context_docs:
            context_text = "\n\n".join(context_docs)
            user_prompt = f"""Context information:
{context_text}

Question: {item.query}

Answer based on the context above. If the context doesn't contain relevant information, say so."""
            
            logger.debug(
                "Using RAG mode",
                extra={
                    "process_step": self.process_step,
                    "query_id": item.query_id,
                    "context_docs_count": len(context_docs)
                }
            )
        else:
            user_prompt = item.query
            
            logger.debug(
                "Using direct mode (no RAG)",
                extra={
                    "process_step": self.process_step,
                    "query_id": item.query_id
                }
            )
        
        # Step 3: Call LLM API
        try:
            response = self.client.chat.completions.create(
                model=settings.model_name,
                messages=[
                    {"role": "system", "content": self.prompt_template.prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=settings.temperature,
                max_tokens=settings.max_tokens
            )
        except Exception as e:
            logger.error(
                "LLM API call failed",
                extra={
                    "process_step": self.process_step,
                    "query_id": item.query_id
                },
                exc_info=True
            )
            raise RuntimeError("Error in LLM API response") from e
        
        # Step 4: Parse and validate response
        try:
            answer = response.choices[0].message.content.strip()
            
            # Validate non-empty response
            if not answer:
                raise ValueError("Empty LLM response")
            
            logger.debug(
                "LLM response successful",
                extra={
                    "process_step": self.process_step,
                    "query_id": item.query_id,
                    "answer_length": len(answer)
                }
            )
            
        except (IndexError, AttributeError, ValueError) as e:
            logger.error(
                "Failed to parse LLM response",
                extra={
                    "process_step": self.process_step,
                    "query_id": item.query_id
                }
            )
            raise RuntimeError("Error parsing LLM response") from e
        
        logger.info(
            "Processor completed",
            extra={
                "process_step": self.process_step,
                "query_id": item.query_id
            }
        )
        
        return ProcessorResult(
            query_id=item.query_id,
            answer=answer,
            sources_used=context_docs if context_docs else []
        )
