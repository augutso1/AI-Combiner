from pydantic import BaseModel
from typing import List

class ChatRequest(BaseModel):
    query: str
    models: List[str] 