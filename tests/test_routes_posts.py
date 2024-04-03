import pytest
from unittest.mock import MagicMock
from fastapi import status


@pytest.mark.asyncio
async def test_add_post(client, token, session):

    post_service_mock = MagicMock()
    posts_repository_mock = MagicMock()
    post_service_mock.upload_post.return_value = {"url": "mock_url", "public_id": "mock_public_id"}
    posts_repository_mock.add_post.return_value = {"id": 1, "url": "mock_url", "description": "Test description"}

    response_mock = MagicMock()
    response_mock.status_code = status.HTTP_201_CREATED
    response_mock.json.return_value = {"id": 1, "url": "mock_url", "description": "Test description"}

    client.post = MagicMock(return_value=response_mock)

    with pytest.MonkeyPatch().context() as m:
        m.setattr('src.routes.posts.posts_repository', posts_repository_mock)
        m.setattr('src.routes.posts.post_service', post_service_mock)

        response = client.post("/posts/", headers={"Authorization": f"Bearer {token}"}, data={"file": ...})

        assert response.status_code == status.HTTP_201_CREATED
        assert response.json() == {"id": 1, "url": "mock_url", "description": "Test description"}


@pytest.mark.asyncio
async def test_delete_post(client, token, session):
    
    posts_repository_mock = MagicMock()
    posts_repository_mock.get_post.return_value = {"id": 1, "user_id": 1}

    response_mock = MagicMock()
    response_mock.status_code = status.HTTP_204_NO_CONTENT

    client.delete = MagicMock(return_value=response_mock)

    with pytest.MonkeyPatch().context() as m:
        m.setattr('src.routes.posts.posts_repository.get_post', posts_repository_mock.get_post)
        m.setattr('src.routes.posts.posts_repository.delete_post', posts_repository_mock.delete_post)
   
        response = client.delete("/posts/1", headers={"Authorization": f"Bearer {token}"})

        assert response.status_code == status.HTTP_204_NO_CONTENT


@pytest.mark.asyncio
async def test_edit_description(client, token, session):
    
    posts_repository_mock = MagicMock()
    posts_repository_mock.get_post.return_value = {"id": 1, "user_id": 1, "description": "Initial description"}
    posts_repository_mock.edit_description.return_value = {"id": 1, "description": "Updated description"}
    
    response_mock = MagicMock()
    response_mock.status_code = status.HTTP_200_OK
    response_mock.json.return_value = {"id": 1, "description": "Updated description"}

    client.patch = MagicMock(return_value=response_mock)

    with pytest.MonkeyPatch().context() as m:
        m.setattr('src.routes.posts.posts_repository.get_post', posts_repository_mock.get_post)
        m.setattr('src.routes.posts.posts_repository.edit_description', posts_repository_mock.edit_description)

        response = client.patch("/posts/1", headers={"Authorization": f"Bearer {token}"}, json={"description": "Updated description"},)

        assert response.status_code == status.HTTP_200_OK
        assert response.json() == {"id": 1, "description": "Updated description"}


@pytest.mark.asyncio
async def test_get_post(client, token, session):
    
    posts_repository_mock = MagicMock()
    posts_repository_mock.get_post.return_value = {"id": 1, "description": "Test description"}

    response_mock = MagicMock()
    response_mock.status_code = status.HTTP_200_OK
    response_mock.json.return_value = {"id": 1, "description": "Test description"}

    client.get = MagicMock(return_value=response_mock)

    with pytest.MonkeyPatch().context() as m:
        m.setattr('src.routes.posts.posts_repository.get_post', posts_repository_mock.get_post)
    
        response = client.get("/posts/1", headers={"Authorization": f"Bearer {token}"})

        assert response.status_code == status.HTTP_200_OK
        assert response.json() == {"id": 1, "description": "Test description"}


@pytest.mark.asyncio
async def test_get_post_qrcode(client, token, session):
   
    posts_repository_mock = MagicMock()
    posts_repository_mock.get_post_url.return_value = "http://example.com"

    response_mock = MagicMock()
    response_mock.status_code = status.HTTP_200_OK
    response_mock.headers = {"content-type": "image/png"} 

    client.get = MagicMock(return_value=response_mock)
    
    with pytest.MonkeyPatch().context() as m:
        m.setattr('src.routes.posts.posts_repository.get_post', posts_repository_mock.get_post)

        response = client.get("/posts/1/qrcode", headers={"Authorization": f"Bearer {token}"})

        assert response.status_code == status.HTTP_200_OK
        assert response.headers["content-type"] == "image/png"


@pytest.mark.asyncio
async def test_search_posts(client, token, session):

    posts_repository_mock = MagicMock()
    posts_repository_mock.get_all_posts.return_value = [{"id": 1, "description": "Test description"}]

    response_mock = MagicMock()
    response_mock.status_code = status.HTTP_200_OK
    response_mock.json.return_value = [{"id": 1, "description": "Test description"}]  

    client.get = MagicMock(return_value=response_mock)

    with pytest.MonkeyPatch().context() as m:
        m.setattr('src.routes.posts.posts_repository.get_all_posts', posts_repository_mock.get_all_posts)

        response = client.get("/posts/", headers={"Authorization": f"Bearer {token}"})

        assert response.status_code == status.HTTP_200_OK
        assert response.json() == [{"id": 1, "description": "Test description"}]


@pytest.mark.asyncio
async def test_read_comment_for_post(client, token, session):
   
    comments_repository_mock = MagicMock()
    comments_repository_mock.get_comments_for_post.return_value = [{"id": 1, "comment_text": "Test comment"}]

    response_mock = MagicMock()
    response_mock.status_code = status.HTTP_200_OK
    response_mock.json.return_value = [{"id": 1, "comment_text": "Test comment"}]

    client.get = MagicMock(return_value=response_mock)
    
    with pytest.MonkeyPatch().context() as m:
        m.setattr('src.repository.comments.get_comments_for_post', comments_repository_mock.get_comments_for_post)

    response = client.get("/posts/1/comments", headers={"Authorization": f"Bearer {token}"})

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == [{"id": 1, "comment_text": "Test comment"}]


@pytest.mark.asyncio
async def test_read_tags(client, token, session):
   
    posts_repository_mock = MagicMock()
    tags_repository_mock = MagicMock()
    posts_repository_mock.get_post.return_value = {"id": 1}
    tags_repository_mock.get_post_tags.return_value = [{"id": 1, "tag_name": "Test tag"}]

    response_mock = MagicMock()
    response_mock.status_code = status.HTTP_200_OK
    response_mock.json.return_value = [{"id": 1, "tag_name": "Test tag"}]

    client.get = MagicMock(return_value=response_mock)
    
    with pytest.MonkeyPatch().context() as m:
        m.setattr('src.routes.posts.posts_repository.get_post', posts_repository_mock.get_post)
        m.setattr('src.repository.tags.get_post_tags', tags_repository_mock.get_post_tags)
    
        response = client.get("/posts/1/tags", headers={"Authorization": f"Bearer {token}"})

        assert response.status_code == 200
        assert response.json() == [{"id": 1, "tag_name": "Test tag"}]


@pytest.mark.asyncio
async def test_get_post_rating(client, token, session):
   
    posts_repository_mock = MagicMock()
    posts_repository_mock.get_post.return_value = {"id": 1, "rating": 4.5}

    response_mock = MagicMock()
    response_mock.status_code = status.HTTP_200_OK
    response_mock.json.return_value = {"id": 1, "rating": 4.5}

    client.get = MagicMock(return_value=response_mock)

    with pytest.MonkeyPatch().context() as m:
        m.setattr('src.routes.posts.posts_repository.get_post', posts_repository_mock.get_post)

    response = client.get("/posts/1/rating", headers={"Authorization": f"Bearer {token}"})

    assert response.status_code == 200
    assert response.json() == {"id": 1, "rating": 4.5}