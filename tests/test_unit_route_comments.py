from pytest import fixture

from src.database.models import User, UserRole
from fastapi import status

@fixture(scope='function')
def token(client, user, session):
    response = client.post("/api/auth/signup",
                           json={"username": "deadpool",
                                 "email": "deadpool@example.com",
                                 "password": "123456789"})
    current_user: User = session.query(User).filter(User.email == user.get('email')).first()
    current_user.role = UserRole.admin
    session.commit()
    response = client.post("/api/auth/login",
                           data={"email": "deadpool@example.com", "password": "123456789"},
                           headers={'Content-Type': 'application/x-www-form-urlencoded'})
    data = response.json()
    return data["access_token"]


def test_create_comment_for_post(client, token):
    response = client.post("/api/comments/1/comments", json={"comment_text": "Test text for comment 1"}, 
                           headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200, response.text
    body_data = response.json()
    assert body_data == {
        "id": 1,
        "comment_text": "Test text for comment 1",
        "created_at": f"{body_data['created_at']}",
        "updated_at": None,
        "user_id": 1,
        "post_id": 1,
    }


def test_read_comment(client, token):
    response = client.get("api/comments/1", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200, response.text
    data = response.json()
    assert data[0]["id"] == 1


def test_read_comment_for_post(client, token):
    response = client.get("api/comments/1/comments", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200, response.text
    data = response.json()
    assert data[0]["id"] == 1


def test_update_existing_comment(client, token):
    response = client.put(
        "api/comments/1", json={"comment_text": "Test text for comment updated"},
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200, response.text
    body_data = response.json()
    assert body_data == {
        "id": 1,
        "comment_text": "Test text for comment updated",
        "created_at": f"{body_data['created_at']}",
        "updated_at": f"{body_data['updated_at']}",
        "user_id": 1,
        "post_id": 1,
    }


def test_delete_existing_comment(client, token):
    response = client.delete("/api/comments/100", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == status.HTTP_404_NOT_FOUND
    response = client.delete("/api/comments/{post_id}", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
