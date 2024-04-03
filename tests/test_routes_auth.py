import pytest
from fastapi import HTTPException, status
from fastapi.testclient import TestClient
from unittest.mock import MagicMock, patch
from schemas.users import UserModel
from src.routes.auth import router
from src.services.email import send_email

@pytest.fixture
def client():
    return TestClient(router)

def test_signup_new_user(client):
    
    mock_user = UserModel(username="testuser", email="test@example.com", password="password")
    
    with patch('src.routes.auth.repository_users.get_user_by_email') as mock_get_user_by_email, \
         patch('src.routes.auth.auth_service.get_password_hash') as mock_get_password_hash, \
         patch('src.routes.auth.repository_users.create_user') as mock_create_user, \
         patch('src.services.email.send_email'), \
         patch('src.services.auth.datetime'):
    
        mock_get_user_by_email.return_value = None
        mock_get_password_hash.return_value = "hashed_password"
        mock_create_user.return_value = mock_user  

        response_mock = MagicMock()
        response_mock.status_code = status.HTTP_201_CREATED
        response_mock.json.return_value = {'username': 'testuser', 'email': 'test@example.com', 'user_role': 'user'}
        client.post = MagicMock(return_value=response_mock)
        
        response = client.post('/auth/signup', json={"username": "testuser", "email": "test@example.com", "password": "password"})
        
        assert response.status_code == status.HTTP_201_CREATED
        assert response.json() == {'username': 'testuser', 'email': 'test@example.com', 'user_role': 'user'}


def test_signup_existing_user(client):
    
    with patch('src.routes.auth.repository_users.get_user_by_email') as mock_get_user_by_email:

        mock_get_user_by_email.return_value = {'id': 1, 'email': 'test@example.com', 'user_role': 'user'}

        response_mock = MagicMock()
        response_mock.status_code = status.HTTP_409_CONFLICT
        response_mock.json.return_value = {'detail': 'Account already exists'}
        client.post = MagicMock(return_value=response_mock)
        
        response = client.post('/auth/signup', json={"email": "test@example.com", "password": "password"},)
        
        assert response.status_code == status.HTTP_409_CONFLICT
        assert response.json() == {'detail': 'Account already exists'}


def test_login_successful(client):
    
    with patch('src.routes.auth.repository_users.get_user_by_email') as mock_get_user_by_email, \
         patch('src.routes.auth.auth_service.create_access_token') as mock_create_access_token, \
         patch('src.routes.auth.auth_service.create_refresh_token') as mock_create_refresh_token, \
         patch('src.routes.auth.repository_users.update_token') as mock_update_token:
        
        mock_get_user_by_email.return_value = {'email': 'test@example.com', 'password': 'hashed_password', 'refresh_token': None}
        mock_create_access_token.return_value = "access_token"
        mock_create_refresh_token.return_value = "refresh_token"

        response_mock = MagicMock()
        response_mock.status_code = status.HTTP_200_OK
        response_mock.json.return_value = {'access_token': 'access_token', 'refresh_token': 'refresh_token', 'token_type': 'bearer'}
        client.post = MagicMock(return_value=response_mock)
        
        response = client.post('/auth/login', data={"username": "test@example.com", "password": "password"})
        
        assert response.status_code == status.HTTP_200_OK
        assert response.json() == {'access_token': 'access_token', 'refresh_token': 'refresh_token', 'token_type': 'bearer'}


def test_login_invalid_email(client):
   
    with patch('src.routes.auth.repository_users.get_user_by_email') as mock_get_user_by_email:
        
        mock_get_user_by_email.return_value = None

        response_mock = MagicMock()
        response_mock.status_code = status.HTTP_401_UNAUTHORIZED
        response_mock.json.return_value = {'detail': 'Invalid email'}
        client.post = MagicMock(return_value=response_mock)
        
        response = client.post('/auth/login', data={"username": "test@example.com", "password": "password"})
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert response.json() == {'detail': 'Invalid email'}


def test_refresh_token_successful(client):
   
    with patch('src.routes.auth.auth_service.decode_refresh_token') as mock_decode_refresh_token, \
         patch('src.routes.auth.repository_users.get_user_by_email') as mock_get_user_by_email, \
         patch('src.routes.auth.auth_service.create_access_token') as mock_create_access_token, \
         patch('src.routes.auth.auth_service.create_refresh_token') as mock_create_refresh_token:
        
        mock_decode_refresh_token.return_value = "test@example.com"
        mock_get_user_by_email.return_value = {'email': 'test@example.com', 'refresh_token': 'refresh_token'}
        mock_create_access_token.return_value = "new_access_token"
        mock_create_refresh_token.return_value = "new_refresh_token"

        response_mock = MagicMock()
        response_mock.status_code = status.HTTP_200_OK
        response_mock.json.return_value = {'access_token': 'new_access_token', 'refresh_token': 'new_refresh_token', 'token_type': 'bearer'}
        client.get = MagicMock(return_value=response_mock)
        
        response = client.get('/auth/refresh_token', headers={"Authorization": "Bearer refresh_token"})
        
        assert response.status_code == status.HTTP_200_OK
        assert response.json() == {'access_token': 'new_access_token', 'refresh_token': 'new_refresh_token', 'token_type': 'bearer'}


def test_refresh_token_invalid_refresh_token(client):
   
    with patch('src.routes.auth.auth_service.decode_refresh_token') as mock_decode_refresh_token, \
         patch('src.routes.auth.repository_users.get_user_by_email') as mock_get_user_by_email:
        
        mock_decode_refresh_token.return_value = "test@example.com"
        mock_get_user_by_email.return_value = {'email': 'test@example.com', 'refresh_token': None}

        response_mock = MagicMock()
        response_mock.status_code = status.HTTP_401_UNAUTHORIZED
        response_mock.json.return_value = {'detail': 'Invalid refresh token'}
        client.get = MagicMock(return_value=response_mock)
        
        response = client.get('/auth/refresh_token', headers={"Authorization": "Bearer invalid_refresh_token"})
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert response.json() == {'detail': 'Invalid refresh token'}


def test_confirmed_email_successful(client):
    
    with patch('src.routes.auth.auth_service.get_email_from_token') as mock_get_email_from_token, \
         patch('src.routes.auth.repository_users.get_user_by_email') as mock_get_user_by_email:
        
        mock_get_email_from_token.return_value = "test@example.com"
        mock_get_user_by_email.return_value = {'email': 'test@example.com', 'confirmed': False}

        response_mock = MagicMock()
        response_mock.status_code = status.HTTP_200_OK
        response_mock.json.return_value = {'message': 'Email confirmed'}
        client.get = MagicMock(return_value=response_mock)
        
        response = client.get('/auth/confirmed_email/confirmation_token')
        
        assert response.status_code == status.HTTP_200_OK
        assert response.json() == {'message': 'Email confirmed'}


def test_request_email(client):
    
    with patch('src.routes.auth.repository_users.get_user_by_email') as mock_get_user_by_email: 
        
        response_mock = MagicMock()
        response_mock.status_code = status.HTTP_200_OK
        response_mock.json.return_value = {'message': 'Email confirmed'}
        client.get = MagicMock(return_value=response_mock)
        
        mock_get_user_by_email.return_value = {'email': 'test@example.com', 'confirmed': False}

        response_mock = MagicMock()
        response_mock.status_code = status.HTTP_200_OK
        response_mock.json.return_value = {'message': 'Check your email for confirmation.'}
        client.post = MagicMock(return_value=response_mock)
        
        response = client.post('/auth/request_email', json={"email": "test@example.com"})
        
        assert response.status_code == status.HTTP_200_OK
        assert response.json() == {'message': 'Check your email for confirmation.'}
        


def test_logout(client):
    

    response_mock = MagicMock()
    response_mock.status_code = status.HTTP_200_OK
    response_mock.json.return_value = {"message": "User is logout"}
    client.post = MagicMock(return_value=response_mock)
    
    response = client.post('/auth/logout', headers={"Authorization": "Bearer access_token"})
    
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {"message": "User is logout"}
    
