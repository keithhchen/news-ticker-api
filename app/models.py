from pydantic import BaseModel
from typing import Optional, Dict

class GraphInput(BaseModel):
    input_text: str
    parameters: Optional[Dict] = None

    class Config:
        json_schema_extra = {
            "example": {
                "input_text": "Sample input text for analysis",
                "parameters": {"temperature": 0}
            }
        }

class GraphOutput(BaseModel):
    analysis: str
    sentiment: str
    summary: str
    final_report: str 