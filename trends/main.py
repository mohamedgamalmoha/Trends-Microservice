from fastapi import FastAPI
from app.core.lifespan import lifespan
from app.api.endpoints import task


app = FastAPI(lifespan=lifespan)

app.include_router(task.task_router, prefix='/api')
