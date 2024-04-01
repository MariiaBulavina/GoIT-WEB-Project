from pytest import fixture

from src.database.models import Tag, User, UserRole
from fastapi import status


@fixture(scope='module')
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


def test_create_new_tag(client, session, token):
    tags_string = "test"
    response = client.post("/api/tags/1/tags", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == status.HTTP_201_CREATED, response.text

    expected_response = [{"id": 1, "tag": tags_string}]
    assert response.json() == expected_response

    tag = session.query(Tag).first()
    assert tag is not None
    assert tag.tag_name == tags_string


def test_create_new_tag_not_authorization(client, session):
    token = "not_valid"
    response = client.post("/api/tags/1/tags", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == status.HTTP_401_UNAUTHORIZED, response.text


def test_create_new_tag_not_valid_tags(client, session, token):
    response = client.post("/api/tag/", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == status.HTTP_404_NOT_FOUND, response.text


def test_read_tag_found(client, session, token):
    tag = {"id": 1, "tag": "test" }
    response = client.get("/api/tags/test", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == status.HTTP_200_OK, response.text
    assert response.json() == tag


def test_read_tag_not_found(client, session, token):
    tag = None
    response = client.get("/api/tags/testnotfound", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == status.HTTP_404_NOT_FOUND, response.text


def test_update_existing_tag_found(client, session, token):
    new_tag_name = "test_1"
    response = client.put("/api/tags/1", headers={"Authorization": f"Bearer {token}"}, json={"tag_name": new_tag_name})
    assert response.status_code == status.HTTP_200_OK, response.text
    expected_response = {"id": 1, "tag": new_tag_name}
    assert response.json() == expected_response


def test_update_existing_tag_not_found(client, session, token):
    new_tag_name = "test_1"
    response = client.put("/api/tags/1000", headers={"Authorization": f"Bearer {token}"}, json={"tag_name": new_tag_name})
    assert response.status_code == status.HTTP_404_NOT_FOUND, response.text


def test_delete_existing_tag_found(client, session, token):
    response = client.delete("/api/tags/test_1", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == status.HTTP_204_NO_CONTENT, response.text
    tag = session.query(Tag).filter(Tag.tag == "test").first()
    assert tag is None


def test_delete_existing_tag_not_found(client, session, token):
    response = client.delete("/api/tags/test_100", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == status.HTTP_404_NOT_FOUND, response.text
