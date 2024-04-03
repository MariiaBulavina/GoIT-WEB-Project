from unittest.mock import MagicMock

import pytest
from fastapi import status

from src.database.models import User, UserRole
from src.repository import rating as repository_rating


@pytest.mark.asyncio
async def test_create_rating(client, token, session):
   
    repository_rating.create_rating = MagicMock(return_value={"id": 1, "rating": 5})

    user = User(id=1, user_role=UserRole.user)
    session.get_current_user = MagicMock(return_value=user)

    response_mock = MagicMock()
    response_mock.status_code = status.HTTP_201_CREATED
    client.post = MagicMock(return_value=response_mock)

    response = client.post("/rating/", headers={"Authorization": f"Bearer {token}"}, json={"post_id": 1, "rating": 5})

    assert response.status_code == status.HTTP_201_CREATED


@pytest.mark.asyncio
async def test_delete_rating_moderator(client, token, session):
    
    user = User(id=1, user_role=UserRole.moderator)
    session.get_current_user = MagicMock(return_value=user)

    response_mock = MagicMock()
    response_mock.status_code = status.HTTP_204_NO_CONTENT
    client.delete = MagicMock(return_value=response_mock)

    response = client.delete("/rating/", headers={"Authorization": f"Bearer {token}"}, json={"post_id": 1, "user_id": 1})

    assert response.status_code == status.HTTP_204_NO_CONTENT


@pytest.mark.asyncio
async def test_delete_rating_unauthorized_user(client, token, session):
  
    user = User(id=1, user_role=UserRole.user)
    session.get_current_user = MagicMock(return_value=user)

    response_mock = MagicMock()
    response_mock.status_code = status.HTTP_403_FORBIDDEN
    client.delete = MagicMock(return_value=response_mock)

    response = client.delete("/rating/", headers={"Authorization": f"Bearer {token}"}, json={"post_id": 1, "user_id": 1})

    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.asyncio
async def test_get_user_ratings_authenticated_user(client, token, session):
    
    repository_rating.get_user_ratings = MagicMock(return_value=[{"id": 1, "rating": 5}])

    user = User(id=1, user_role=UserRole.user)
    session.get_current_user = MagicMock(return_value=user)

    response_mock = MagicMock()
    response_mock.status_code = status.HTTP_200_OK
    client.get = MagicMock(return_value=response_mock)

    response = client.get("/rating/", headers={"Authorization": f"Bearer {token}"})

    assert response.status_code == status.HTTP_200_OK


@pytest.mark.asyncio
async def test_get_user_ratings_unauthenticated_user(client, token, session):
    
    user = None
    session.get_current_user = MagicMock(return_value=user)

    response_mock = MagicMock()
    response_mock.status_code = status.HTTP_401_UNAUTHORIZED
    client.get = MagicMock(return_value=response_mock)

    response = client.get("/rating/", headers={"Authorization": f"Bearer {token}"})

    assert response.status_code == status.HTTP_401_UNAUTHORIZED