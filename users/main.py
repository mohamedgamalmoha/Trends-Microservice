from fastapi import FastAPI
from app.core.lifespan import lifespan
from app.api.endpoints import auth, users, verification, password


app = FastAPI(lifespan=lifespan)

app.include_router(auth.auth_router, prefix='/api')
app.include_router(users.user_router, prefix='/api')
app.include_router(verification.email_verification_router, prefix='/api')
app.include_router(password.password_reset_router, prefix='/api')
