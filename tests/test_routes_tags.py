from unittest.mock import MagicMock

import pytest
from fastapi import status

from src.database.models import User, UserRole

from src.repository import tags as tags_repository
from src.repository import posts as posts_repository


@pytest.mark.asyncio
async def test_create_new_tag_authenticated_user(client, token, session):
    
    tags_repository.create_tag = MagicMock(return_value={"id": 1, "name": "Test Tag"})
    posts_repository.get_post = MagicMock(return_value={"id": 1, "title": "Test Post"})

    response_mock = MagicMock()
    response_mock.status_code = status.HTTP_201_CREATED
    client.post = MagicMock(return_value=response_mock)
   
    response = client.post("/tags/", headers={"Authorization": f"Bearer {token}"}, json={"post_id": 1, "tag": {"name": "Test Tag"}},)

    assert response.status_code == status.HTTP_201_CREATED


@pytest.mark.asyncio
async def test_create_new_tag_unauthenticated_user(client, token, session):
   
    user = None
    session.get_current_user = MagicMock(return_value=user)

    response_mock = MagicMock()
    response_mock.status_code = status.HTTP_401_UNAUTHORIZED
    client.post = MagicMock(return_value=response_mock)
   
    response = client.post("/tags/",  headers={"Authorization": f"Bearer {token}"}, json={"post_id": 1, "tag": {"name": "Test Tag"}},)

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    

@pytest.mark.asyncio
async def test_read_existing_tag(client, token, session):
   
    tags_repository.get_tag_by_name = MagicMock(return_value={"id": 1, "name": "Test Tag"})

    user = User(id=1, user_role=UserRole.user)
    session.get_current_user = MagicMock(return_value=user)

    response_mock = MagicMock()
    response_mock.status_code = status.HTTP_200_OK
    response_mock.json.return_value = {"id": 1, "name": "Test Tag"}
    client.get = MagicMock(return_value=response_mock)

    response = client.get("/tags/Test_Tag", headers={"Authorization": f"Bearer {token}"})

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {"id": 1, "name": "Test Tag"}


@pytest.mark.asyncio
async def test_read_non_existing_tag(client, token, session):
   
    tags_repository.get_tag_by_name = MagicMock(return_value=None)

    user = User(id=1, user_role=UserRole.user)
    session.get_current_user = MagicMock(return_value=user)

    response_mock = MagicMock()
    response_mock.status_code = status.HTTP_404_NOT_FOUND
    client.get = MagicMock(return_value=response_mock)

    response = client.get("/tags/Non_Existing_Tag", headers={"Authorization": f"Bearer {token}"})

    assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.asyncio
async def test_update_existing_tag_authenticated_user(client, token, session):
  
    tags_repository.update_tag = MagicMock(return_value={"id": 1, "name": "Updated Tag"})

    user = User(id=1, user_role=UserRole.admin)
    session.get_current_user = MagicMock(return_value=user)

    response_mock = MagicMock()
    response_mock.status_code = status.HTTP_200_OK
    response_mock.json.return_value = {"id": 1, "name": "Updated Tag"}
    client.put = MagicMock(return_value=response_mock)

    response = client.put("/tags/1", headers={"Authorization": f"Bearer {token}"}, json={"name": "Updated Tag"},)

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {"id": 1, "name": "Updated Tag"}


@pytest.mark.asyncio
async def test_delete_existing_tag_admin(client, token, session):
    
    user = User(id=1, user_role=UserRole.admin)
    session.get_current_user = MagicMock(return_value=user)

    response_mock = MagicMock()
    response_mock.status_code = status.HTTP_204_NO_CONTENT
    client.delete = MagicMock(return_value=response_mock)

    response = client.delete("/tags/1", headers={"Authorization": f"Bearer {token}"})

    assert response.status_code == status.HTTP_204_NO_CONTENT


@pytest.mark.asyncio
async def test_delete_existing_tag_authenticated_user(client, token, session):
    
    user = User(id=1, user_role=UserRole.user)
    session.get_current_user = MagicMock(return_value=user)

    response_mock = MagicMock()
    response_mock.status_code = status.HTTP_403_FORBIDDEN
    client.delete = MagicMock(return_value=response_mock)

    response = client.delete("/tags/1", headers={"Authorization": f"Bearer {token}"})

    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.asyncio
async def test_delete_existing_tag_unauthenticated_user(client, token, session):
    
    user = None
    session.get_current_user = MagicMock(return_value=user)

    response_mock = MagicMock()
    response_mock.status_code = status.HTTP_401_UNAUTHORIZED
    client.delete = MagicMock(return_value=response_mock)

    response = client.delete("/tags/1", headers={"Authorization": f"Bearer {token}"})

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
