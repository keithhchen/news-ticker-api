from pydantic import BaseModel
from typing import Optional, List

class GraphInput(BaseModel):
    input_text: str
    parameters: Optional[dict] = None

    class Config:
        schema_extra = {
            "example": {
                "input_text": "Sample input",
                "parameters": {"param1": "value1"}
            }
        } 