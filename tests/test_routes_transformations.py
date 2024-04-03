from typing import Any, AsyncGenerator, Literal
from unittest.mock import MagicMock

from fastapi import status
import pytest
from sqlalchemy.orm import Session

from src.database.models import User
from src.services.auth import auth_service
from src.database.db import get_db



async def mock_resize_post(post_id: int, width: int, height: int, user: User, db: Session) -> Any:
    return {"transformed_post_url": f"https://example.com/post/{post_id}/resized"}


async def mock_add_filter(post_id: int, filter: Literal[..., ...], user: User, db: Session) -> Any:
    return {"transformed_post_url": f"https://example.com/post/{post_id}/filtered"}


def mock_generate_qrcode(url: str) -> AsyncGenerator:
    yield b"mocked_qr_code_image"


@pytest.mark.asyncio
async def test_resize_post(client, session) -> None:
    
    session.get_db = get_db
    
    session.auth_service = MagicMock()
    session.post_service = MagicMock()
    session.generate_qrcode = MagicMock()

    session.auth_service.get_current_user = auth_service.get_current_user
    session.post_service.resize_post = mock_resize_post
    session.generate_qrcode = mock_generate_qrcode

    response_mock = MagicMock()
    response_mock.status_code = status.HTTP_201_CREATED
    response_mock.headers = {"content-type": "image/png"}
    response_mock.content = b"mocked_qr_code_image"
    client.post = MagicMock(return_value=response_mock)

    response = client.post(
        "/transformations/resize/1",
        json={"width": 100, "height": 100},
        headers={"Authorization": "Bearer mock_access_token"},
    )

    assert response.status_code == status.HTTP_201_CREATED
    assert response.headers["content-type"] == "image/png"
    assert response.content == b"mocked_qr_code_image"


@pytest.mark.asyncio
async def test_add_filter_to_post(client: Any, session: Any) -> None:
  
    session.get_db = get_db

    session.auth_service = MagicMock()
    session.post_service = MagicMock()
    session.generate_qrcode = MagicMock()
    
    session.auth_service.get_current_user = auth_service.get_current_user
    session.post_service.add_filter = mock_add_filter
    session.generate_qrcode = mock_generate_qrcode

    response_mock = MagicMock()
    response_mock.status_code = status.HTTP_201_CREATED
    response_mock.headers = {"content-type": "image/png"}
    response_mock.content = b"mocked_qr_code_image"
    client.post = MagicMock(return_value=response_mock)

    response = client.post(
        "/transformations/filter/1",
        json={"filter": "al_dente"},
        headers={"Authorization": "Bearer mock_access_token"},
    )

    assert response.status_code == status.HTTP_201_CREATED
    assert response.headers["content-type"] == "image/png"
    assert response.content == b"mocked_qr_code_image"
