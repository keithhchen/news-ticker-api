from fastapi import APIRouter, HTTPException
from ..models.text_model import TextRequest, TextResponse
from ..services.text_service import TextService

router = APIRouter(prefix="/api/v1")
text_service = TextService()

@router.post("/text", response_model=TextResponse)
async def process_text(request: TextRequest):
    try:
        response = await text_service.process_text(request)
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 