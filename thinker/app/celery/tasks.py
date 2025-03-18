from typing import Dict, Optional, Any

import httpx
from celery import shared_task

from app.core.conf import settings
from app.utils import split_think_content


@shared_task(
    max_retries=5,
    default_retry_delay=1
)
async def think_task(
        question: str,
        context: Optional[str] = None,
        temperature: Optional[float] = 0.7,
        max_tokens: Optional[int] = 250,
    ) -> Dict[str, Any]:

    if context:
        prompt = f"""
        Context: {context}

        Question: {question}

        Please provide a concise and accurate answer based on the context provided.
        """
    else:
        prompt = f"""
        Question: {question}

        Please provide a concise and accurate answer based on your knowledge.
        """

    ollama_request = {
        "model": settings.OLLAMA_MODEL_NAME,
        "prompt": prompt,
        "temperature": temperature,
        "max_tokens": max_tokens,
        "stream": False
    }

    async with httpx.AsyncClient(timeout=settings.OLLAMA_REQUEST_TIMEOUT) as client:
        response = await client.post(f"{settings.OLLAMA_API_URL}/generate", json=ollama_request)

        if response.status_code != 200:
            raise Exception(f"Failed to generate think content: {response.text}")

        result = response.json()
        text = result.get("response", "").strip()
        think_content, remaining_content = split_think_content(text)

        return {
            "answer": remaining_content,
            "thinking": think_content
        }
