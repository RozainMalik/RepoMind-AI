from fastapi import APIRouter
from pydantic import BaseModel
from app.routes import chat
from app.services.chat_service import ChatService

router = APIRouter(
    prefix="/chat",
    tags=["Chat"]
)

chat_service = ChatService()

class ChatRequest(BaseModel):
    repository_id: int
    question: str

@router.post("/")
def chat(request: ChatRequest):

    response = chat_service.ask(
        request.question,
        request.repository_id,
    )

    return response