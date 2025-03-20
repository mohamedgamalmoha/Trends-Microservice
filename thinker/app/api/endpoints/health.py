import httpx
from fastapi import APIRouter, HTTPException, status
from shared_utils import messages

from app.core.conf import settings
from app.schemas.health import Health


health_router = APIRouter(
    prefix='/health',
    tags = ['health']
)


@health_router.get("/", response_model=Health)
async def health_check():
    try:
        async with httpx.AsyncClient(timeout=settings.OLLAMA_REQUEST_TIMEOUT) as client:
            response = await client.get(f"{settings.OLLAMA_API_URL}/tags")
            if response.status_code == 200:
                models = response.json().get("models", [])
                model_exists = any(model["name"] == settings.OLLAMA_MODEL_NAME for model in models)
                if not model_exists:
                    raise HTTPException(
                        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                        detail=messages.OLLAMA_MODEL_IS_NOT_LOADED
                    )
                return Health(
                    message=messages.OLLAMA_SERVICE_IS_RUNNING
                )
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=messages.OLLAMA_SERVICE_RETURNED_UNEXPECTED_RESPONSE
            )
    except httpx.RequestError:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=messages.CANNOT_CONNECT_TO_OLLAMA_SERVICE
        )
