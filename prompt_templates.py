# prompt_templates.py
from pydantic import BaseModel
from datetime import datetime
from typing import List

class PromptTemplate(BaseModel):
    name: str
    version: str
    prompt: str
    last_modified: datetime
    tested_models: List[str]
    author: str = "Unknown"
    description: str = ""