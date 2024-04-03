import os
import sys
from dotenv import load_dotenv
import asyncio

import unittest
from unittest.mock import MagicMock, patch
from fastapi import HTTPException, status
from sqlalchemy.orm import Session

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
load_dotenv()

from src.repository import tags  # noqa: E402
from src.schemas.tags import TagModel  # noqa: E402
from src.database.models import Tag  # noqa: E402


class TestTagRepository(unittest.IsolatedAsyncioTestCase):

    async def test_create_tag(self):
        mock_db = MagicMock(spec=Session)
        tag_data = TagModel(tag="Test Tag")

        # Case 1: Tag length is 0
        tag_data.tag = ""
        tags.get_tag_by_name = MagicMock(return_value=asyncio.sleep(0, None))
        with self.assertRaises(HTTPException) as context:
            await tags.create_tag(mock_db, tag_data)
        self.assertEqual(context.exception.status_code, status.HTTP_400_BAD_REQUEST)

        # Case 2: Tag created successfully
        tag_data.tag = "New Test Tag"
        tags.get_tag_by_name = MagicMock(return_value=asyncio.sleep(0, None))
        created_tag = await tags.create_tag(mock_db, tag_data)
        self.assertEqual(created_tag.tag, tag_data.tag)

    @patch('src.repository.tags.Session')
    async def test_update_tag(self, mock_session):
        mock_db = MagicMock()
        tag_data = TagModel(tag="Updated Tag")
        tag_id = 1

        # Case 1: Tag not found
        mock_query = MagicMock()
        mock_query.filter.return_value.first.return_value = None
        mock_db.query.return_value = mock_query

        with self.assertRaises(HTTPException) as context:
            await tags.update_tag(mock_db, tag_id, tag_data)
        self.assertEqual(context.exception.status_code, status.HTTP_404_NOT_FOUND)

        # Case 2: New tag already exists
        mock_query.filter.return_value.first.return_value = Tag(id=tag_id, tag="Existing Tag")
        mock_query.filter.return_value.first.return_value = Tag(id=2, tag=tag_data.tag)
        with self.assertRaises(HTTPException) as context:
            await tags.update_tag(mock_db, tag_id, tag_data)
        self.assertEqual(context.exception.status_code, status.HTTP_400_BAD_REQUEST)

        # Case 3: Tag length is 0
        tag_data.tag = ""
        with self.assertRaises(HTTPException) as context:
            await tags.update_tag(mock_db, tag_id, tag_data)
        self.assertEqual(context.exception.status_code, status.HTTP_400_BAD_REQUEST)

    async def test_delete_tag(self):
        mock_db = MagicMock(spec=Session)
        tag_id = 1

        # Case 1: Tag not found
        mock_query = MagicMock()
        mock_query.filter.return_value.first.return_value = None
        mock_db.query.return_value = mock_query
        with self.assertRaises(HTTPException) as context:
            await tags.delete_tag(mock_db, tag_id)
        self.assertEqual(context.exception.status_code, status.HTTP_404_NOT_FOUND)

        # Case 2: Tag deleted successfully
        mock_query = MagicMock()
        mock_query.filter.return_value.first.return_value = Tag(id=tag_id, tag="Tag to Delete")
        mock_db.query.return_value = mock_query
        deleted_tag = await tags.delete_tag(mock_db, tag_id)
        self.assertEqual(deleted_tag.id, tag_id)


if __name__ == '__main__':
    unittest.main()
