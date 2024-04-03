import pytest
from unittest.mock import MagicMock
from fastapi import status

from src.repository import posts as posts_repository
from src.repository import comments as comments_repository


@pytest.mark.asyncio
async def test_create_comment_for_post(client, token, session):
    
    comments_repository.create_comment = MagicMock(return_value={"id": 1, "comment_text": "Test comment"})
    posts_repository.get_post = MagicMock(return_value={"id": 1, "title": "Test post"})
    
    response_mock = MagicMock()
    response_mock.status_code = status.HTTP_201_CREATED
    client.post = MagicMock(return_value=response_mock)
   
    response = client.post("/comments/", headers={"Authorization": f"Bearer {token}"}, json={"post_id": 1, "comment_data": {"text": "Test comment"}})
    
    assert response.status_code == status.HTTP_201_CREATED


@pytest.mark.asyncio
async def test_read_comment(client, token, session):
   
    comments_repository.get_comment = MagicMock(return_value={"id": 1, "comment_text": "Test comment"})

    response_mock = MagicMock()
    response_mock.status_code = status.HTTP_200_OK

    response_mock.json.return_value = {"id": 1, "comment_text": "Test comment"}

    client.get = MagicMock(return_value=response_mock)

    response = client.get("/comments/1", headers={"Authorization": f"Bearer {token}"})

    assert response.status_code == status.HTTP_200_OK

    data = response.json()
    assert data == {"id": 1, "comment_text": "Test comment"}


@pytest.mark.asyncio
async def test_update_existing_comment(client, token, session):
  
    comments_repository.update_comment = MagicMock(return_value={"id": 1, "comment_text": "Updated comment"})

    response_mock = MagicMock()
    response_mock.status_code = status.HTTP_200_OK

    response_mock.json.return_value = {"id": 1, "comment_text": "Updated comment"}

    client.put = MagicMock(return_value=response_mock)

    response =  client.put("/comments/1", headers={"Authorization": f"Bearer {token}"}, json={"comment_data": {"text": "Updated comment"}})

    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data == {"id": 1, "comment_text": "Updated comment"}


@pytest.mark.asyncio
async def test_delete_existing_comment(client, token, session):
    
    comments_repository.delete_comment = MagicMock(return_value={"id": 1})

    response_mock = MagicMock()
    response_mock.status_code = status.HTTP_204_NO_CONTENT

    client.delete = MagicMock(return_value=response_mock)

    response =  client.delete("/comments/1", headers={"Authorization": f"Bearer {token}"})

    assert response.status_code == status.HTTP_204_NO_CONTENT
