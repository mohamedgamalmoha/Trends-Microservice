from fastapi import FastAPI

from db import lifespan
from routes import auth_router, user_router


app = FastAPI(lifespan=lifespan)

app.include_router(auth_router, prefix='/api')
app.include_router(user_router, prefix='/api')
