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


@fixture(scope='function')
def token_second(client, user, session):
    response = client.post("/api/auth/signup",
                           json={"username": "deadpool",
                                 "email": "deadpool@example.com",
                                 "password": "123456789"})
    current_user: User = session.query(User).filter(User.email == 'testpool@example.com').first()
    current_user.role = UserRole.admin
    session.commit()
    response = client.post("/api/auth/login",
                           data={"username": "testpool@example.com", "password": "testpassword"},
                           headers={'Content-Type': 'application/x-www-form-urlencoded'})
    data = response.json()
    return data["access_token"]


def test_get_current_user(client, token):
    response = client.get("api/users/me/", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == status.HTTP_200_OK
    response = client.get("api/users/me/")
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_get_user_profile(client, token, user):
    username = user['username']
    response = client.get(f"api/users/{username}/", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == status.HTTP_200_OK
    username = 'wrong_username'
    response = client.get(f"api/users/{username}/", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == status.HTTP_404_NOT_FOUND

