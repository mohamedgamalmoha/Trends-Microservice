import pytest
from tests.factories import UserCreateFactoryDict


def test_create_user(client):
    # Generate user data
    user_data = UserCreateFactoryDict()

    # Make API request to create user
    response = client.post("/api/v1/users/", json=user_data)
    data = response.json()

    # Assert response
    assert response.status_code == 201
    assert 'id' in data
    assert "date_created" in data
    assert data['id'] is not None
    assert data["email"] == user_data["email"]
    assert data["username"] == user_data["username"]


def test_create_user_invalid_email(client):
    # Generate user data with invalid email
    user_data = UserCreateFactoryDict()
    user_data["email"] = "invalid_email"

    # Make API request to create user
    response = client.post("/api/v1/users/", json=user_data)
    data = response.json()

    # Assert response
    assert response.status_code == 422
    assert data['detail'][0]['msg'] == "value is not a valid email address: An email address must have an @-sign."


def test_get_user_token(client):
    # Generate user data
    user_data = UserCreateFactoryDict()

    # Make API request to create user
    response = client.post("/api/v1/users/", json=user_data)
    assert response.status_code == 201

    # Make API request to get user token
    response = client.post("/api/v1/jwt/create/", json={"email": user_data["email"], "password": user_data["password"]})
    data = response.json()

    # Assert response
    assert response.status_code == 200
    assert 'access_token' in data
    assert 'token_type' in data
    assert data['access_token'] is not None
    assert data['token_type'] is not None
    assert data['token_type'] == "Bearer"


def test_verify_user_token(client):
    # Generate user data
    user_data = UserCreateFactoryDict()

    # Make API request to create user
    response = client.post("/api/v1/users/", json=user_data)
    assert response.status_code == 201

    # Make API request to get user token
    response = client.post("/api/v1/jwt/create/", json={"email": user_data["email"], "password": user_data["password"]})
    data = response.json()
    access_token = data['access_token']

    # Make API request to verify token
    response = client.get("/api/v1/jwt/verify/", headers={"Authorization": f"Bearer {access_token}"})

    # Assert response
    assert response.status_code == 204


def test_get_user(client):
    # Generate user data
    user_data = UserCreateFactoryDict()

    # Make API request to create user
    response = client.post("/api/v1/users/", json=user_data)
    assert response.status_code == 201

    # Make API request to get user token
    response = client.post("/api/v1/jwt/create/", json={"email": user_data["email"], "password": user_data["password"]})
    data = response.json()
    access_token = data['access_token']

    # Make API request to get user
    response = client.get("/api/v1/users/me/", headers={"Authorization": f"Bearer {access_token}"})
    data = response.json()

    # Assert response
    assert response.status_code == 200
    assert data['id'] is not None
    assert data["email"] == user_data["email"]
    assert data["username"] == user_data["username"]


def test_get_user_invalid_token(client):
    # Generate user data
    user_data = UserCreateFactoryDict()

    # Make API request to create user
    response = client.post("/api/v1/users/", json=user_data)
    assert response.status_code == 201

    # Make API request to get user token
    response = client.post("/api/v1/jwt/create/", json={"email": user_data["email"], "password": user_data["password"]})
    data = response.json()
    access_token = data['access_token']

    # Make API request to get user with invalid token
    response = client.get("/api/v1/users/me/", headers={"Authorization": f"Bearer {access_token}invalid"})
    data = response.json()

    # Assert response
    assert response.status_code == 401
    assert data['detail'] == "Invalid Token"


def test_get_user_expired_token(client):
    # Generate user data
    user_data = UserCreateFactoryDict()

    # Make API request to create user
    response = client.post("/api/v1/users/", json=user_data)
    assert response.status_code == 201

    # Make API request to get user token
    response = client.post("/api/v1/jwt/create/", json={"email": user_data["email"], "password": user_data["password"]})
    data = response.json()
    access_token = data['access_token']

    # Simulate token expiration (this is just a placeholder, actual implementation may vary)
    expired_token = access_token + "expired"

    # Make API request to get user with expired token
    response = client.get("/api/v1/users/me/", headers={"Authorization": f"Bearer {expired_token}"})
    data = response.json()

    # Assert response
    assert response.status_code == 401
    assert data['detail'] == "Invalid Token"


def test_get_user_unauthorized(client):
    # Make API request to get user without authentication
    response = client.get("/api/v1/users/me/")
    data = response.json()

    # Assert response
    assert response.status_code == 403
    assert data['detail'] == "Not authenticated"


def test_get_user_not_found(client):
    # Generate user data
    user_data = UserCreateFactoryDict()

    # Make API request to create user
    response = client.post("/api/v1/users/", json=user_data)
    assert response.status_code == 201

    # Make API request to get user token
    response = client.post("/api/v1/jwt/create/", json={"email": user_data["email"], "password": user_data["password"]})
    data = response.json()
    access_token = data['access_token']

    # Make API request to get user with invalid ID
    response = client.get("/api/v1/users/9999999/", headers={"Authorization": f"Bearer {access_token}"})
    data = response.json()

    # Assert response
    assert response.status_code == 404
    assert data['detail'] == "User not found"


@pytest.mark.asyncio
async def test_get_user_list(async_client): 
    from shared_utils.db.session import get_db
    from app.repositories.user import get_user_repository
    
    user_data = UserCreateFactoryDict(is_admin=True)
    user_data.pop("password_confirm")

    db = await anext(get_db())

    # Create an admin user
    user_repository = get_user_repository(db=db)
    await user_repository.create_admin(**user_data)
    
    # Make API request to get user token - use await with async client
    response = await async_client.post(
        "/api/v1/jwt/create/", 
        json={"email": user_data["email"], "password": user_data["password"]}
    )
    data = response.json()
    access_token = data['access_token']

    # Make API request to get user list - use await with async client
    response = await async_client.get(
        "/api/v1/users/", 
        headers={"Authorization": f"Bearer {access_token}"}
    )
    data = response.json()

    # Assert response
    assert response.status_code == 200
    assert isinstance(data['results'], list)
    assert len(data['results']) > 0

    await db.close()  # Close the database connection


@pytest.mark.asyncio
async def test_get_user_list_pagination(async_client):
    from shared_utils.db.session import get_db
    from app.repositories.user import get_user_repository
    
    total_users = 15

    db = await anext(get_db())
    user_repository = get_user_repository(db=db)
    
    # Create default users 
    for _ in range(total_users - 1):
        user_data = UserCreateFactoryDict()
        user_data.pop("password_confirm")
        await user_repository.create(**user_data)

    # Create admin user
    admin_data = UserCreateFactoryDict(is_admin=True)
    admin_data.pop("password_confirm")
    await user_repository.create_admin(**admin_data)

    # Make API request to get user token - use await with async client
    response = await async_client.post(
        "/api/v1/jwt/create/",
        json={"email": admin_data["email"], "password": admin_data["password"]}
    )
    data = response.json()
    access_token = data['access_token']
    
    # Get first page of users (default size to 10)
    response = await async_client.get(
        "/api/v1/users/", 
        headers={"Authorization": f"Bearer {access_token}"}
    )
    data = response.json()

    assert response.status_code == 200
    assert isinstance(data['results'], list)
    assert len(data['results']) == 10
    assert data['total_count'] == total_users
    assert data['next_page'] == 2
    assert data['previous_page'] is None

    # Get second page of users
    response = await async_client.get(
        "/api/v1/users/", 
        headers={"Authorization": f"Bearer {access_token}"},
        params={'page': 2}
    )
    data = response.json()

    assert response.status_code == 200
    assert isinstance(data['results'], list)
    assert len(data['results']) == total_users - 10
    assert data['total_count'] == total_users
    assert data['next_page'] is None
    assert data['previous_page'] == 1

    await db.close()  # Close the database connection


def test_get_user_list_unauthorized(client):
    # Make API request to get user list without authentication
    response = client.get("/api/v1/users/")
    data = response.json()

    # Assert response
    assert response.status_code == 403
    assert data['detail'] == "Not authenticated"


def test_update_user(client):   
    # Generate user data
    user_data = UserCreateFactoryDict()
    
    # Make API request to create user   
    response = client.post("/api/v1/users/", json=user_data)
    assert response.status_code == 201
    user_id = response.json()["id"]

    # Make API request to get user token
    response = client.post("/api/v1/jwt/create/", json={"email": user_data["email"], "password": user_data["password"]})
    assert response.status_code == 200
    data = response.json()
    access_token = data['access_token']     
    
    # Make API request to update user
    response = client.put(f"/api/v1/users/{user_id}/", headers={"Authorization": f"Bearer {access_token}"}, json={"first_name": "new_first_name"})
    data = response.json()
    
    # Assert response
    assert response.status_code == 200
    assert data['id'] is not None
    assert data["email"] == user_data["email"]
    assert data["first_name"] == "new_first_name"


def test_delete_user(client):
    # Generate user data
    user_data = UserCreateFactoryDict()

    # Make API request to create user
    response = client.post("/api/v1/users/", json=user_data)
    assert response.status_code == 201
    user_id = response.json()["id"]

    # Make API request to get user token
    response = client.post("/api/v1/jwt/create/", json={"email": user_data["email"], "password": user_data["password"]})
    assert response.status_code == 200
    data = response.json()
    access_token = data['access_token']

    # Make API request to delete user
    response = client.delete(f"/api/v1/users/{user_id}/", headers={"Authorization": f"Bearer {access_token}"})

    # Assert response
    assert response.status_code == 204
    assert response.content == b""
