import pytest
from fastapi import status
from unittest.mock import MagicMock
from src.database.models import User, UserRole


@pytest.mark.asyncio
async def test_get_current_user(client, session):

    user = User(id=1, email="test@example.com", user_role=UserRole.user)

    session.auth_service = MagicMock()
    session.auth_service.get_current_user = MagicMock(return_value=user)

    response_mock = MagicMock()
    response_mock.status_code = status.HTTP_200_OK
    response_mock.json.return_value = {"id": 1, "email": "test@example.com", "user_role": "user"}
    client.get = MagicMock(return_value=response_mock)
    
    response = client.get("/users/me")
    
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {"id": 1, "email": "test@example.com", "user_role": "user"}


@pytest.mark.asyncio
async def test_update_avatar_user_authenticated_user(client, session):

    user = User(id=1, email="test@example.com", user_role=UserRole.user)

    session.auth_service = MagicMock()
    session.repositories_users = MagicMock()
    session.auth_service.get_current_user = MagicMock(return_value=user)
    session.repositories_users.update_avatar_url = MagicMock(return_value=user)
    
    response_mock = MagicMock()
    response_mock.status_code = status.HTTP_200_OK
    client.patch = MagicMock(return_value=response_mock)
    
    response = client.patch("/users/me", files={"file": ("image.png", b"image_content")})
    
    assert response.status_code == status.HTTP_200_OK


@pytest.mark.asyncio
async def test_get_user_profile_existing_user(client, session):

    session.repositories_users = MagicMock()

    session.repositories_users.get_user_by_username = MagicMock(return_value=User(id=1, username="test_user"))
    session.repositories_users.get_user_profile = MagicMock(return_value={"id": 1, "username": "test_user"})

    response_mock = MagicMock()
    response_mock.status_code = status.HTTP_200_OK
    response_mock.json.return_value = {"id": 1, "username": "test_user"}
    client.get = MagicMock(return_value=response_mock)
    
    response = client.get("/users/?username=test_user")
    
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {"id": 1, "username": "test_user"}


@pytest.mark.asyncio
async def test_get_user_profile_non_existing_user(client, session):

    session.repositories_users = MagicMock()

    session.repositories_users.get_user_by_username = MagicMock(return_value=None)

    response_mock = MagicMock()
    response_mock.status_code = status.HTTP_404_NOT_FOUND
    client.get = MagicMock(return_value=response_mock)
    
    response = client.get("/users/?username=non_existing_user")
    
    assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.asyncio
async def test_get_user_by_id_existing_user(client, session):

    user = User(id=1, email="test@example.com", user_role=UserRole.user)

    session.auth_service = MagicMock()
    session.repositories_users = MagicMock()

    session.auth_service.get_current_user = MagicMock(return_value=user)
    session.repositories_users.get_user_by_id = MagicMock(return_value=user)
    session.repositories_users.get_user_profile = MagicMock(return_value={"id": 1, "email": "test@example.com"})

    response_mock = MagicMock()
    response_mock.status_code = status.HTTP_200_OK
    response_mock.json.return_value = {"id": 1, "email": "test@example.com"}
    client.get = MagicMock(return_value=response_mock)

    response = client.get("/users/1")
    
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {"id": 1, "email": "test@example.com"}


@pytest.mark.asyncio
async def test_get_user_by_id_non_existing_user(client, session):

    user = User(id=1, email="test@example.com", user_role=UserRole.user)

    session.auth_service = MagicMock()
    session.repositories_users = MagicMock()

    session.auth_service.get_current_user = MagicMock(return_value=user)
    session.repositories_users.get_user_by_id = MagicMock(return_value=None)

    response_mock = MagicMock()
    response_mock.status_code = status.HTTP_404_NOT_FOUND
    client.get = MagicMock(return_value=response_mock)
    
    response = client.get("/users/2")
    
    assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.asyncio
async def test_manage_user_change_role_admin(client, session):

    user = User(id=1, email="test@example.com", user_role=UserRole.admin)

    session.auth_service = MagicMock()
    session.repositories_users = MagicMock()

    session.auth_service.get_current_user = MagicMock(return_value=user)
    session.repositories_users.get_user_by_id = MagicMock(return_value=User(id=2, email="user@example.com"))
    session.repositories_users.change_role = MagicMock(return_value=User(id=2, email="user@example.com", user_role=UserRole.admin))

    response_mock = MagicMock()
    response_mock.status_code = status.HTTP_200_OK
    response_mock.json.return_value =  {"user": {"id": 2, "email": "user@example.com", "user_role": "admin"}, "detail": "User has been changed to admin"}
    client.patch = MagicMock(return_value=response_mock)
    
    response = client.patch("/users/2", json={"action": "change_user_role", "role": "admin"})
    
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {"user": {"id": 2, "email": "user@example.com", "user_role": "admin"}, "detail": "User has been changed to admin"}


@pytest.mark.asyncio
async def test_get_user_posts(client, session):

    user = User(id=1, email="test@example.com", user_role=UserRole.user)

    session.auth_service = MagicMock()
    session.posts_repository = MagicMock()

    session.auth_service.get_current_user = MagicMock(return_value=user)
    session.posts_repository.get_user_posts = MagicMock(return_value=[{"id": 1, "title": "Test Post"}])

    response_mock = MagicMock()
    response_mock.status_code = status.HTTP_200_OK
    response_mock.json.return_value = [{"id": 1, "title": "Test Post"}]
    client.get = MagicMock(return_value=response_mock)
    
    response = client.get("/users/1/posts")
    
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == [{"id": 1, "title": "Test Post"}]