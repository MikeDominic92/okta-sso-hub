"""
Tests for Okta Client Wrapper

Unit tests for the OktaClientWrapper class.
Note: These are example tests. In production, use mocks to avoid hitting real Okta API.
"""

import pytest
import asyncio
from unittest.mock import Mock, patch, AsyncMock
import sys
import os

# Add parent directory to path to import okta_client
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'automation', 'python'))

from okta_client import OktaClientWrapper


class TestOktaClientWrapper:
    """Test suite for OktaClientWrapper"""

    @pytest.fixture
    def okta_client(self):
        """Fixture to create OktaClientWrapper instance"""
        with patch.dict(os.environ, {
            'OKTA_DOMAIN': 'dev-test.okta.com',
            'OKTA_API_TOKEN': 'test_token_123'
        }):
            return OktaClientWrapper()

    def test_initialization(self, okta_client):
        """Test client initialization"""
        assert okta_client.config['orgUrl'] == 'https://dev-test.okta.com'
        assert okta_client.config['token'] == 'test_token_123'
        assert okta_client.client is not None

    def test_initialization_without_credentials(self):
        """Test initialization fails without credentials"""
        with patch.dict(os.environ, {}, clear=True):
            with pytest.raises(ValueError, match='OKTA_DOMAIN and OKTA_API_TOKEN must be set'):
                OktaClientWrapper()

    @pytest.mark.asyncio
    async def test_get_user(self, okta_client):
        """Test getting user by ID"""
        mock_user = Mock()
        mock_user.id = 'user123'
        mock_user.profile.email = 'test@example.com'

        with patch.object(okta_client.client, 'get_user', return_value=(mock_user, None, None)):
            user = await okta_client.get_user('user123')
            assert user.id == 'user123'
            assert user.profile.email == 'test@example.com'

    @pytest.mark.asyncio
    async def test_get_user_error(self, okta_client):
        """Test error handling when getting user"""
        with patch.object(okta_client.client, 'get_user', return_value=(None, None, 'User not found')):
            with pytest.raises(Exception, match='Error fetching user'):
                await okta_client.get_user('invalid_id')

    @pytest.mark.asyncio
    async def test_list_users(self, okta_client):
        """Test listing users"""
        mock_user1 = Mock()
        mock_user1.profile.email = 'user1@example.com'

        mock_user2 = Mock()
        mock_user2.profile.email = 'user2@example.com'

        async def mock_user_iterator():
            yield mock_user1
            yield mock_user2

        with patch.object(okta_client.client, 'list_users', return_value=(mock_user_iterator(), None, None)):
            users = await okta_client.list_users()
            assert len(users) == 2
            assert users[0].profile.email == 'user1@example.com'

    @pytest.mark.asyncio
    async def test_create_user(self, okta_client):
        """Test creating a user"""
        user_profile = {
            'firstName': 'John',
            'lastName': 'Doe',
            'email': 'john.doe@example.com',
            'login': 'john.doe@example.com'
        }

        mock_user = Mock()
        mock_user.id = 'newuser123'
        mock_user.profile.email = 'john.doe@example.com'

        with patch.object(okta_client.client, 'create_user', return_value=(mock_user, None, None)):
            user = await okta_client.create_user(user_profile)
            assert user.id == 'newuser123'
            assert user.profile.email == 'john.doe@example.com'

    @pytest.mark.asyncio
    async def test_update_user(self, okta_client):
        """Test updating a user"""
        mock_user = Mock()
        mock_user.profile = Mock()
        mock_user.profile.firstName = 'John'
        mock_user.profile.lastName = 'Doe'

        updated_user = Mock()
        updated_user.profile = Mock()
        updated_user.profile.firstName = 'Jane'
        updated_user.profile.lastName = 'Doe'

        with patch.object(okta_client.client, 'get_user', return_value=(mock_user, None, None)):
            with patch.object(okta_client.client, 'update_user', return_value=(updated_user, None, None)):
                user = await okta_client.update_user('user123', {'firstName': 'Jane'})
                assert user.profile.firstName == 'Jane'

    @pytest.mark.asyncio
    async def test_deactivate_user(self, okta_client):
        """Test deactivating a user"""
        with patch.object(okta_client.client, 'deactivate_user', return_value=(None, None)):
            result = await okta_client.deactivate_user('user123')
            assert result is True

    @pytest.mark.asyncio
    async def test_list_groups(self, okta_client):
        """Test listing groups"""
        mock_group1 = Mock()
        mock_group1.profile.name = 'Developers'

        mock_group2 = Mock()
        mock_group2.profile.name = 'Admins'

        async def mock_group_iterator():
            yield mock_group1
            yield mock_group2

        with patch.object(okta_client.client, 'list_groups', return_value=(mock_group_iterator(), None, None)):
            groups = await okta_client.list_groups()
            assert len(groups) == 2
            assert groups[0].profile.name == 'Developers'

    @pytest.mark.asyncio
    async def test_create_group(self, okta_client):
        """Test creating a group"""
        mock_group = Mock()
        mock_group.id = 'group123'
        mock_group.profile.name = 'QA Team'

        with patch.object(okta_client.client, 'create_group', return_value=(mock_group, None, None)):
            group = await okta_client.create_group('QA Team', 'Quality Assurance team')
            assert group.id == 'group123'
            assert group.profile.name == 'QA Team'

    @pytest.mark.asyncio
    async def test_add_user_to_group(self, okta_client):
        """Test adding user to group"""
        with patch.object(okta_client.client, 'add_user_to_group', return_value=(None, None)):
            result = await okta_client.add_user_to_group('group123', 'user123')
            assert result is True

    @pytest.mark.asyncio
    async def test_remove_user_from_group(self, okta_client):
        """Test removing user from group"""
        with patch.object(okta_client.client, 'remove_user_from_group', return_value=(None, None)):
            result = await okta_client.remove_user_from_group('group123', 'user123')
            assert result is True


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
