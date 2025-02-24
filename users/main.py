from fastapi import FastAPI
from app.db.lifespan import lifespan
from app.api.endpoints import auth, users


app = FastAPI(lifespan=lifespan)

app.include_router(auth.auth_router, prefix='/api')
app.include_router(users.user_router, prefix='/api')
