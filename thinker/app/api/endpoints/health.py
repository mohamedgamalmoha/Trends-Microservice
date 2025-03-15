import httpx
from fastapi import APIRouter

from app.core.conf import settings
from app.schemas.health import Health, HealthStatusEnum


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
                print(models)
                model_exists = any(model["name"] == settings.OLLAMA_MODEL_NAME for model in models)
                if not model_exists:
                    return {
                        "status": HealthStatusEnum.WARNING,
                        "message": f"Ollama is running but {settings.OLLAMA_MODEL_NAME} is not loaded."
                    }
                return {
                    "status": HealthStatusEnum.OK,
                    "message": "Ollama service is running with Deep Seek model loaded"
                }
            return {
                "status": HealthStatusEnum.ERROR,
                "message": "Ollama service returned unexpected response"
            }
    except httpx.RequestError:
        return {
            "status": HealthStatusEnum.ERROR,
            "message": "Cannot connect to Ollama service"
        }
