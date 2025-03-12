from pydantic import BaseModel
from typing import Optional, Dict

class TextRequest(BaseModel):
    content: str
    metadata: Optional[Dict] = None

    class Config:
        json_schema_extra = {
            "example": {
                "content": "Sample text content",
                "metadata": {"source": "user_input"}
            }
        }

class TextResponse(BaseModel):
    id: str
    content: str
    processed: bool
    metadata: Optional[Dict] = None 