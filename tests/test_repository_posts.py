import os
import sys
from dotenv import load_dotenv

import unittest
from unittest.mock import MagicMock, patch
from datetime import datetime
from sqlalchemy.orm import Session

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
load_dotenv()

from src.repository import posts
from src.database.models import User, Post, Tag, TransformedPost


class TestPostsRepository(unittest.IsolatedAsyncioTestCase):
    @patch('src.repository.posts.datetime')
    async def test_add_post(self, mock_datetime):
      
        mock_datetime.now.return_value = datetime(2022, 1, 1)
        mock_session = MagicMock(spec=Session)
        mock_user = MagicMock(spec=User)
        mock_user.id = 1

        with patch('src.repository.posts.cloudinary.uploader') as mock_uploader:
    
            result = await posts.add_post("post_url", "public_id", "description", mock_user, mock_session)

            mock_session.add.assert_called_once()
            mock_session.commit.assert_called_once()
            mock_session.refresh.assert_called_once()

            self.assertIsInstance(result, Post)
            self.assertEqual(result.post_url, "post_url")
            self.assertEqual(result.public_id, "public_id")
            self.assertEqual(result.description, "description")
            self.assertEqual(result.user_id, 1)
            self.assertEqual(result.created_at, datetime(2022, 1, 1))
            self.assertEqual(result.updated_at, datetime(2022, 1, 1))

    @patch('src.repository.posts.datetime')
    async def test_delete_post(self, mock_datetime):
     
        mock_datetime.now.return_value = datetime(2022, 1, 1)

        mock_session = MagicMock(spec=Session)
        mock_post = MagicMock(spec=Post)
        mock_post.public_id = "public_id"
        mock_session.query().filter().first.return_value = mock_post

        with patch('src.repository.posts.cloudinary.uploader') as mock_uploader:
            
            result = await posts.delete_post(1, mock_session)

            mock_session.query().filter().first.assert_called_once()
            mock_session.delete.assert_called_once_with(mock_post)
            mock_session.commit.assert_called_once()
            mock_uploader.destroy.assert_called_once_with("public_id")

            self.assertEqual(result, mock_post)

    @patch('src.repository.posts.datetime')
    async def test_edit_description(self, mock_datetime):
        
        mock_datetime.now.return_value = datetime(2022, 1, 1)

        mock_session = MagicMock(spec=Session)
        mock_post = MagicMock(spec=Post)
        mock_post.description = "old_description"
        mock_session.query().filter().first.return_value = mock_post

        result = await posts.edit_description(1, "new_description", mock_session)

        mock_session.query().filter().first.assert_called_once()
        mock_session.commit.assert_called_once()

        self.assertEqual(result, mock_post)
        self.assertEqual(result.description, "new_description")
        self.assertEqual(result.updated_at, datetime(2022, 1, 1))

    async def test_get_posts(self):
       
        mock_session = MagicMock(spec=Session)
        mock_posts = [MagicMock(spec=Post), MagicMock(spec=Post)]
        mock_session.query().all.return_value = mock_posts

        result = await posts.get_posts(mock_session)

        mock_session.query().all.assert_called_once()

        self.assertIsInstance(result, list)
        self.assertIsInstance(result[0], Post)
        self.assertIsInstance(result[1], Post)

    async def test_get_my_posts(self):
     
        mock_session = MagicMock(spec=Session)
        mock_user = MagicMock(spec=User)
        mock_user.id = 1
        mock_posts = [MagicMock(spec=Post), MagicMock(spec=Post)]
        mock_session.query().filter().all.return_value = mock_posts

        result = await posts.get_my_posts(mock_user, mock_session)

        mock_session.query().filter().all.assert_called_once()

        self.assertIsInstance(result, list)
        self.assertIsInstance(result[0], Post)
        self.assertIsInstance(result[1], Post)

    async def test_get_post(self):
       
        mock_session = MagicMock(spec=Session)
        mock_post = MagicMock(spec=Post)
        mock_session.query().filter().first.return_value = mock_post

        result = await posts.get_post(1, mock_session)

        mock_session.query().filter().first.assert_called_once()

        self.assertEqual(result, mock_post)

    async def test_get_post_url(self):
     
        mock_session = MagicMock(spec=Session)
        mock_post = MagicMock(spec=Post)
        mock_post.post_url = "post_url"
        mock_session.query().filter().first.return_value = mock_post

        result = await posts.get_post_url(1, mock_session)

        mock_session.query().filter().first.assert_called_once()

        self.assertEqual(result, "post_url")

    async def test_add_tag_to_post(self):
    
        mock_session = MagicMock(spec=Session)

        mock_post = MagicMock(spec=Post)
        mock_post.tags = []
        mock_tag = MagicMock(spec=Tag)
        mock_tag.tag = "tag"

        result = await posts.add_tag_to_post(mock_post, mock_tag, mock_session)

        mock_session.commit.assert_called_once()
        mock_session.refresh.assert_called_once_with(mock_post)

        self.assertEqual(result, mock_post)
        self.assertIn(mock_tag, mock_post.tags)

    async def test_get_post_by_url(self):
     
        mock_session = MagicMock(spec=Session)
        mock_post = MagicMock(spec=Post)
        mock_session.query().filter().first.return_value = mock_post

        result = await posts.get_post_by_url("post_url", mock_session)

        mock_session.query().filter().first.assert_called_once()

        self.assertEqual(result, mock_post)

    async def test_add_transformed_post(self):

        mock_session = MagicMock(spec=Session)

        with patch('src.repository.posts.datetime') as mock_datetime:
            mock_datetime.now.return_value = datetime(2022, 1, 1)

            result = await posts.add_transformed_post("transformed_post_url", 1, mock_session)

        mock_session.add.assert_called_once()
        mock_session.commit.assert_called_once()
        mock_session.refresh.assert_called_once()

        self.assertIsInstance(result, TransformedPost)
        self.assertEqual(result.transformed_post_url, "transformed_post_url")
        self.assertEqual(result.post_id, 1)
        self.assertIsInstance(result.created_at, datetime)
        self.assertEqual(result.created_at, datetime(2022, 1, 1))

    async def test_get_transformed_post_url(self):
     
        mock_session = MagicMock(spec=Session)
        mock_transformed_post = MagicMock(spec=TransformedPost)
        mock_transformed_post.transformed_post_url = "transformed_post_url"
        mock_session.query().filter().first.return_value = mock_transformed_post

        result = await posts.get_transformed_post_url(1, mock_session)

        mock_session.query().filter().first.assert_called_once()

        self.assertEqual(result, "transformed_post_url")

if __name__ == '__main__':
    unittest.main()