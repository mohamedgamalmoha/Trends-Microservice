import time

import httpx
from fastapi import APIRouter, HTTPException

from app.core.conf import settings
from app.utils import split_think_content
from app.schemas.question import Question, Answer


question_router = APIRouter(
    prefix='/question',
    tags=['question']
)


@question_router.post("/answer", response_model=Answer)
async def answer_question(request: Question):
    # Prepare prompt based on whether context is provided
    if request.context:
        prompt = f"""
        Context: {request.context}

        Question: {request.question}

        Please provide a concise and accurate answer based on the context provided.
        """
    else:
        prompt = f"""
        Question: {request.question}

        Please provide a concise and accurate answer based on your knowledge.
        """

    # Prepare request to Ollama
    ollama_request = {
        "model": settings.OLLAMA_MODEL_NAME,
        "prompt": prompt,
        "temperature": request.temperature,
        "max_tokens": request.max_tokens,
        "stream": False
    }

    try:
        async with httpx.AsyncClient() as client:
            start_time = time.perf_counter()
            response = await client.post(f"{settings.OLLAMA_API_URL}/generate", json=ollama_request)
            elapsed = time.perf_counter() - start_time

            if response.status_code != 200:
                raise HTTPException(status_code=response.status_code, detail="Error from Ollama API")

            result = response.json()
            text = result.get("response", "").strip()
            think_content, remaining_content = split_think_content(text)
         
            return {
                "answer": remaining_content,
                "think": think_content,
                "model": settings.OLLAMA_MODEL_NAME,
                "elapsed_time": elapsed
            }
    except httpx.RequestError:
        raise HTTPException(status_code=503, detail="Cannot connect to Ollama service")
