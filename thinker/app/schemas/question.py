from typing import Optional

import pydantic

from app.core.conf import settings


class Question(pydantic.BaseModel):
    question: str = pydantic.Field(
        ...,
        min_length=3,
        max_length=500,
        description="The question to be answered (3-500 characters)"
    )
    context: Optional[str] = pydantic.Field(
        None,
        max_length=2000,
        description="Optional context to provide background information for the question"
    )
    temperature: Optional[float] = pydantic.Field(
        0.7,
        ge=0.0,
        le=2.0,
        description="Controls randomness in generation. Lower = more deterministic (0.0-2.0)"
    )
    max_tokens: Optional[int] = pydantic.Field(
        250,
        ge=10,
        le=512,
        description="Maximum number of output tokens to generate (10-512)"
    )


class Answer(pydantic.BaseModel):
    answer: str
    think: str
    elapsed_time: float
    model: str = settings.OLLAMA_MODEL_NAME
