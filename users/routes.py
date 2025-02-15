from fastapi import HTTPException, status, Request, Response, Header

from main import app
from auth import hash_password, verify_password
from schema import UserCreate, UserUpdate, UserRetrieve
from query import get_user_by_id, get_user_by_username, get_user_by_email


@app.post('/api/login', status_code=status.HTTP_201_CREATED)
async def login(user_data: UserCreate):
    ...


@app.post('/api/users', status_code=status.HTTP_201_CREATED)
async def create_user(user: UserCreate, request: Request, response: Response, request_user_id: str = Header(None)):
    ...


@app.get('/api/users/{user_id}', status_code=status.HTTP_200_OK)
async def get_user(user_id: int, request: Request, response: Response, request_user_id: str = Header(None)):
    ...


@app.get('/api/users', status_code=status.HTTP_200_OK)
async def get_users(request: Request, response: Response, request_user_id: str = Header(None)):
    ...


@app.delete('/api/users/{user_id}', status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(user_id: int, request: Request, response: Response, request_user_id: str = Header(None)):
    ...


@app.put('/api/users/{user_id}', status_code=status.HTTP_200_OK)
async def update_user(user_id: int, user: UserUpdate, request: Request, response: Response,
                      request_user_id: str = Header(None)):
    ...
