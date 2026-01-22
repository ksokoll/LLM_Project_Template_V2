# prompts.py
from prompt_templates import PromptTemplate
from datetime import datetime

SYSTEM_PROMPT = PromptTemplate(
    name="system",
    version="1.0.0",
    prompt="""You are a helpful AI assistant...""",
    last_modified=datetime(2026, 1, 22),
    tested_models=["gpt-4o-mini", "gpt-4o"],
    author="X",
    description="General Q&A"
)

SYSTEM_RAG_PROMPT = PromptTemplate(
    name="system_rag",
    version="1.0.0",
    prompt="""You are a helpful AI assistant with context...""",
    last_modified=datetime(2026, 1, 22),
    tested_models=["gpt-4o-mini"],
    author="X",
    description="RAG optimized"
)