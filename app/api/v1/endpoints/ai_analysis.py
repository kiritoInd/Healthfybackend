from fastapi import APIRouter, Depends
from app.services.ai_service import analyze_with_gpt, analyze_with_groq
from app.db.schemas import PromptRequest

router = APIRouter()

@router.post("/analyze/gpt")
async def analyze_with_gpt_endpoint(request: PromptRequest):
    response = analyze_with_gpt(request.prompt)
    return {"response": response}

@router.post("/analyze/groq")
async def analyze_with_groq_endpoint(request: PromptRequest):
    response = analyze_with_groq(request.prompt)
    return {"response": response}