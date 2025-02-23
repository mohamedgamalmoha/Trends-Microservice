from fastapi import FastAPI
from app.db import lifespan

app = FastAPI(lifespan=lifespan)


from app.api.endpoints import auth, users


app.include_router(auth.auth_router, prefix='/api')
app.include_router(users.user_router, prefix='/api')
