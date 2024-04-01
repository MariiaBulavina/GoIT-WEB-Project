import os
import sys
from dotenv import load_dotenv

import unittest
from unittest.mock import MagicMock
from sqlalchemy.orm.session import Session

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
load_dotenv()

from src.repository import users
from src.database.models import User, UserRole
from src.schemas.users import UserModel


class TestUserRepository(unittest.IsolatedAsyncioTestCase):

    async def test_get_user_by_email(self):
        
        mock_db_session = MagicMock(spec=Session)
        mock_user = MagicMock(spec=User)

        mock_db_session.query().filter().first.return_value = mock_user
    
        result = await users.get_user_by_email("test@example.com", mock_db_session)
        
        self.assertEqual(result, mock_user)
       
        mock_db_session.query.assert_called()
        mock_db_session.query().filter().first.assert_called_once()

    async def test_create_user(self):
        
        mock_db_session = MagicMock(spec=Session)
        user_model = UserModel(username="testuser", email="test@example.com", password="password")
        
        result = await users.create_user(user_model, mock_db_session)
        
        self.assertIsInstance(result, User)
        
        mock_db_session.add.assert_called_once()
        mock_db_session.commit.assert_called_once()
        mock_db_session.refresh.assert_called_once()

    async def test_update_token(self):
        
        mock_db_session = MagicMock(spec=Session)
        mock_user = MagicMock(spec=User)
        
        await users.update_token(mock_user, "new_token", mock_db_session)
        
        mock_user.refresh_token = "new_token"
        mock_db_session.commit.assert_called_once()

    async def test_confirmed_email(self):
       
        mock_db_session = MagicMock(spec=Session)
        mock_user = MagicMock(spec=User)
       
        await users.confirmed_email("test@example.com", mock_db_session)
        
        mock_user.confirmed = True
        mock_db_session.commit.assert_called_once()

    async def test_update_avatar_url(self):
      
        mock_db_session = MagicMock(spec=Session)
        mock_user = MagicMock(spec=User)

        mock_db_session.query().filter().first.return_value = mock_user
      
        result = await users.update_avatar_url("test@example.com", "http://example.com/avatar.jpg", mock_db_session)

        expected_user = MagicMock(spec=User)
        expected_user.avatar = "http://example.com/avatar.jpg"

        self.assertEqual(result.avatar, expected_user.avatar)

        mock_db_session.query.assert_called()
        mock_db_session.query().filter.assert_called()
        mock_db_session.query().filter().first.assert_called_once()
        
        mock_db_session.commit.assert_called_once()

    async def test_get_user_by_username(self):
        
        mock_db_session = MagicMock(spec=Session)
        mock_user = MagicMock(spec=User)
        
        mock_db_session.query().filter().first.return_value = mock_user
        
        result = await users.get_user_by_username("test_user", mock_db_session)
       
        self.assertEqual(result, mock_user)
        
        mock_db_session.query.assert_called()
        mock_db_session.query().filter().first.assert_called_once()

    async def test_get_user_by_id(self):
        
        mock_db_session = MagicMock(spec=Session)
        mock_user = MagicMock(spec=User)
        
        mock_db_session.query().filter().first.return_value = mock_user
        
        result = await users.get_user_by_id(1, mock_db_session)
        
        self.assertEqual(result, mock_user)
        
        mock_db_session.query.assert_called()
        mock_db_session.query().filter().first.assert_called_once()

    async def test_change_role(self):
        
        mock_db_session = MagicMock(spec=Session)
        mock_user = MagicMock(spec=User)
        mock_user.email = "test@example.com"
        
        mock_db_session.query().filter().first.return_value = mock_user
       
        result = await users.change_role("test@example.com", UserRole.admin, mock_db_session)
        
        self.assertEqual(result, mock_user)
        self.assertEqual(result.user_role, UserRole.admin)
        
        mock_db_session.query.assert_called()
        mock_db_session.query().filter().first.assert_called_once()
        mock_db_session.commit.assert_called_once()

    async def test_ban_user(self):
        
        mock_db_session = MagicMock(spec=Session)
        mock_user = MagicMock(spec=User)
        mock_user.email = "test@example.com"
        
        mock_db_session.query().filter().first.return_value = mock_user
        
        result = await users.ban_user("test@example.com", mock_db_session)
        
        self.assertEqual(result, mock_user)
        self.assertEqual(result.is_active, False)
        
        mock_db_session.query.assert_called()

        mock_db_session.query().filter().first.assert_called_once()
        mock_db_session.commit.assert_called_once()

    async def test_unban_user(self):
        
        mock_db_session = MagicMock(spec=Session)
        mock_user = MagicMock(spec=User)
        mock_user.email = "test@example.com"
        mock_user.is_active = False
        
        mock_db_session.query().filter().first.return_value = mock_user
        
        result = await users.unban_user("test@example.com", mock_db_session)
       
        self.assertEqual(result, mock_user)
        self.assertEqual(result.is_active, True)
       
        mock_db_session.query.assert_called()
        mock_db_session.query().filter().first.assert_called_once()
        mock_db_session.commit.assert_called_once()

    async def test_get_user_profile(self):
        
        mock_db_session = MagicMock(spec=Session)
        mock_user = MagicMock(spec=User)
        
        mock_user.id = 1
        mock_user.username = "test_user"
        mock_user.email = "test@example.com"
        mock_user.confirmed = True
        mock_user.avatar = "http://example.com/avatar.jpg"
        mock_user.user_role = UserRole.user
        mock_user.is_active = True
        
        mock_db_session.execute.return_value.scalar.side_effect = [5, 10]
        
        result = await users.get_user_profile(mock_user, mock_db_session)
       
        self.assertIsNotNone(result)
       
        self.assertEqual(mock_user.id, result.id)
        self.assertEqual(mock_user.username, result.username)
        self.assertEqual(mock_user.email, result.email)
        self.assertEqual(mock_user.confirmed, result.confirmed)
        self.assertEqual(mock_user.avatar, result.avatar)
        self.assertEqual(mock_user.user_role, result.user_role)
        self.assertEqual(mock_user.is_active, result.is_active)
        self.assertEqual(5, result.posts_number)
        self.assertEqual(10, result.comments_number)

    async def test_add_to_blacklist(self):
        
        mock_db_session = MagicMock(spec=Session)
       
        await users.add_to_blacklist("token123", mock_db_session)
        
        mock_db_session.add.assert_called_once()
        mock_db_session.commit.assert_called_once()
        mock_db_session.refresh.assert_called_once()

    async def test_is_blacklisted_token(self):
       
        mock_db_session = MagicMock(spec=Session)
       
        mock_db_session.query().filter().first.return_value = None
        
        result = await users.is_blacklisted_token("token123", mock_db_session)
        
        self.assertFalse(result)
       
        mock_db_session.query.filter.assert_called

if __name__ == '__main__':
    unittest.main()