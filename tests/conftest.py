from unittest.mock import MagicMock

import pytest
from starlette.testclient import TestClient
from sqlalchemy.orm import Session


@pytest.fixture(scope='function')
def client():
    return MagicMock(TestClient)

@pytest.fixture(scope='function')
def token(client, session):
    
    response_mock = MagicMock()
    response_mock.json.return_value = {"access_token": "mock_access_token"}

    client.return_value.post.return_value = response_mock

    return "mock_access_token"


@pytest.fixture(scope='function')
def session():
    return MagicMock(Session)