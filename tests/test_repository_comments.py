import os
import sys
from dotenv import load_dotenv

import unittest
from unittest.mock import MagicMock, patch
from datetime import datetime
from sqlalchemy.orm import Session

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
load_dotenv()

from src.repository import comments
from src.schemas.comments import CommentModel
from src.database.models import User, Comment


class TestComments(unittest.IsolatedAsyncioTestCase):

    @patch('src.repository.comments.datetime')
    async def test_create_comment(self, mock_datetime):
       
        mock_datetime.now.return_value = datetime(2022, 1, 1)
        mock_session = MagicMock(spec=Session)
        mock_user = MagicMock(spec=User)
        mock_user.id = 1

        comment_data = CommentModel(comment_text="Test comment")

        result = await comments.create_comment(mock_session, 1, comment_data, mock_user)

        mock_session.add.assert_called_once_with(result)
        mock_session.commit.assert_called_once()
        mock_session.refresh.assert_called_once_with(result)

        self.assertIsInstance(result, Comment)
        self.assertEqual(result.comment_text, "Test comment")
        self.assertEqual(result.created_at, datetime(2022, 1, 1))
        self.assertEqual(result.post_id, 1)
        self.assertEqual(result.user_id, 1)

    async def test_get_comment(self):

        mock_session = MagicMock(spec=Session)
        mock_comment = MagicMock(spec=Comment)
        mock_session.query().filter().first.return_value = mock_comment

        result = await comments.get_comment(mock_session, 1)

        mock_session.query().filter().first.assert_called_once()

        self.assertIsInstance(result, Comment)

    async def test_update_comment(self):

        mock_session = MagicMock(spec=Session)
        mock_comment = MagicMock(spec=Comment)
        mock_session.query().filter().first.return_value = mock_comment

        mock_user = MagicMock(spec=User)
        mock_user.id = 1

        comment_data = CommentModel(comment_text="Updated comment")

        result = await comments.update_comment(mock_session, 1, comment_data, mock_user)

        mock_session.query().filter().first.assert_called_once()
        mock_session.commit.assert_called_once()
        mock_session.refresh.assert_called_once_with(result)

        self.assertIsInstance(result, Comment)
        self.assertEqual(result.comment_text, "Updated comment")

    async def test_delete_comment(self):
        
        mock_session = MagicMock(spec=Session)
        mock_comment = MagicMock(spec=Comment)
        mock_session.query().filter().first.return_value = mock_comment

        result = await comments.delete_comment(mock_session, 1)

        mock_session.query().filter().first.assert_called_once()
        mock_session.delete.assert_called_once_with(mock_comment)
        mock_session.commit.assert_called_once()

        self.assertIsInstance(result, Comment)

    async def test_get_comments_for_post(self):
        
        mock_session = MagicMock(spec=Session)
        mock_comments = [MagicMock(spec=Comment), MagicMock(spec=Comment)]
        mock_session.query().filter().all.return_value = mock_comments

        result = await comments.get_comments_for_post(1, mock_session)

        mock_session.query().filter().all.assert_called_once()

        self.assertIsInstance(result, list)
        self.assertIsInstance(result[0], Comment)
        self.assertIsInstance(result[1], Comment)



if __name__ == '__main__':
    unittest.main()