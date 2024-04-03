import os
import sys
from dotenv import load_dotenv

import unittest
from unittest.mock import MagicMock, patch
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from decimal import Decimal

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
load_dotenv()

from src.repository import rating  # noqa: E402
from src.database.models import PostRating, User, Post  # noqa: E402


class TestRatingRepository(unittest.IsolatedAsyncioTestCase):

    async def test_create_rating(self):
        mock_session = MagicMock(spec=Session)
        mock_user = MagicMock(spec=User)
        mock_user.id = 1
        mock_post = MagicMock(spec=Post)
        mock_post.id = 1
        mock_post.user_id = 2
        
        with patch('src.repository.rating.calculate_average_rating') as mock_calculate_average_rating:
            mock_calculate_average_rating.return_value = Decimal(4.5)

            mock_session.query().filter().first.side_effect = [mock_post, None]

            result = await rating.create_rating(mock_session, 1, 5, mock_user)

            mock_session.add.assert_called_once()
            mock_session.refresh.assert_called_once_with(result)

            self.assertIsInstance(result, PostRating)
            self.assertEqual(result.rating, 5)
            self.assertEqual(result.post_id, 1)
            self.assertEqual(result.user_id, 1)

            mock_calculate_average_rating.assert_called_once_with(1, mock_session)

    async def test_create_rating_post_not_found(self):
    
        mock_session = MagicMock(spec=Session)
        mock_user = MagicMock(spec=User)
        mock_user.id = 1

        mock_session.query().filter().first.return_value = None  

        with self.assertRaises(HTTPException) as context:
            await rating.create_rating(mock_session, 1, 5, mock_user)
    
        self.assertEqual(context.exception.status_code, status.HTTP_404_NOT_FOUND)

    async def test_delete_rating(self):
        mock_session = MagicMock(spec=Session)
        mock_user = MagicMock(spec=User)
        mock_user.id = 1
        mock_post = MagicMock(spec=Post)
        mock_post.id = 1

        mock_rating = MagicMock(spec=PostRating)

        mock_session.query().filter().first.return_value = mock_rating

        result = await rating.delete_rating(1, 1, mock_session)

        self.assertEqual(result, mock_rating)
        mock_session.delete.assert_called_once_with(mock_rating)
        

    async def test_calculate_average_rating(self):
        mock_session = MagicMock(spec=Session)
        mock_session.execute.return_value.scalar.return_value = 4.5

        result = await rating.calculate_average_rating(1, mock_session)

        self.assertEqual(result, Decimal(4.5))

    async def test_get_user_ratings(self):
        mock_session = MagicMock(spec=Session)
        mock_ratings = [MagicMock(spec=PostRating), MagicMock(spec=PostRating)]
        mock_session.query().filter().all.return_value = mock_ratings

        result = await rating.get_user_ratings(1, mock_session)

        self.assertEqual(result, mock_ratings)

    async def test_get_user_ratings_not_found(self):
        mock_session = MagicMock(spec=Session)
        mock_session.query().filter().all.return_value = []

        with self.assertRaises(HTTPException) as context:
            await rating.get_user_ratings(1, mock_session)
        
        self.assertEqual(context.exception.status_code, status.HTTP_404_NOT_FOUND)


if __name__ == '__main__':
    unittest.main()