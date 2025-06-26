from fastapi import APIRouter
from fastapi.responses import StreamingResponse, JSONResponse
from ..services.combiner import chat_stream, get_available_models
from ..schemas.chat import ChatRequest

router = APIRouter()

@router.get("/models")
async def get_models():
    """Retorna a lista de modelos disponíveis do arquivo models.txt."""
    return JSONResponse(content={"models": get_available_models()})

@router.post("/chat")
async def chat_endpoint(request: ChatRequest):
    """Endpoint para streaming de respostas de chat dos modelos selecionados."""
    return StreamingResponse(
        chat_stream(request.query, request.models),
        media_type="text/plain"
    )
