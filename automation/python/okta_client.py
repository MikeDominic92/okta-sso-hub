"""
Okta Client Wrapper

Reusable wrapper around Okta SDK for common operations.
Provides simplified interface for user and group management.
"""

import os
import asyncio
from okta.client import Client as OktaClient
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class OktaClientWrapper:
    """Wrapper class for Okta SDK client"""

    def __init__(self):
        """Initialize Okta client with credentials from environment"""
        self.config = {
            'orgUrl': f'https://{os.getenv("OKTA_DOMAIN")}',
            'token': os.getenv('OKTA_API_TOKEN')
        }

        if not self.config['orgUrl'] or not self.config['token']:
            raise ValueError('OKTA_DOMAIN and OKTA_API_TOKEN must be set in environment')

        self.client = OktaClient(self.config)

    async def get_user(self, user_id):
        """Get user by ID"""
        user, resp, err = await self.client.get_user(user_id)
        if err:
            raise Exception(f'Error fetching user: {err}')
        return user

    async def list_users(self, limit=200, query=None):
        """List users with optional query filter"""
        users, resp, err = await self.client.list_users({'limit': limit, 'q': query})
        if err:
            raise Exception(f'Error listing users: {err}')

        all_users = []
        async for user in users:
            all_users.append(user)

        return all_users

    async def create_user(self, user_profile, activate=True):
        """
        Create new user

        Args:
            user_profile: Dictionary with user profile data
            activate: Whether to activate user immediately

        Returns:
            Created user object
        """
        from okta.models import UserProfile, CreateUserRequest

        profile = UserProfile(user_profile)
        user_req = CreateUserRequest({'profile': profile})

        user, resp, err = await self.client.create_user(user_req, {'activate': activate})
        if err:
            raise Exception(f'Error creating user: {err}')

        return user

    async def update_user(self, user_id, profile_updates):
        """Update user profile"""
        user = await self.get_user(user_id)

        # Update profile fields
        for key, value in profile_updates.items():
            setattr(user.profile, key, value)

        updated_user, resp, err = await self.client.update_user(user_id, user)
        if err:
            raise Exception(f'Error updating user: {err}')

        return updated_user

    async def deactivate_user(self, user_id):
        """Deactivate user"""
        resp, err = await self.client.deactivate_user(user_id)
        if err:
            raise Exception(f'Error deactivating user: {err}')
        return True

    async def delete_user(self, user_id):
        """Delete user (must be deactivated first)"""
        resp, err = await self.client.deactivate_or_delete_user(user_id)
        if err:
            raise Exception(f'Error deleting user: {err}')
        return True

    async def list_groups(self, query=None):
        """List groups with optional query"""
        groups, resp, err = await self.client.list_groups({'q': query})
        if err:
            raise Exception(f'Error listing groups: {err}')

        all_groups = []
        async for group in groups:
            all_groups.append(group)

        return all_groups

    async def get_group(self, group_id):
        """Get group by ID"""
        group, resp, err = await self.client.get_group(group_id)
        if err:
            raise Exception(f'Error fetching group: {err}')
        return group

    async def create_group(self, name, description=''):
        """Create new group"""
        from okta.models import Group, GroupProfile

        profile = GroupProfile({'name': name, 'description': description})
        group = Group({'profile': profile})

        created_group, resp, err = await self.client.create_group(group)
        if err:
            raise Exception(f'Error creating group: {err}')

        return created_group

    async def add_user_to_group(self, group_id, user_id):
        """Add user to group"""
        resp, err = await self.client.add_user_to_group(group_id, user_id)
        if err:
            raise Exception(f'Error adding user to group: {err}')
        return True

    async def remove_user_from_group(self, group_id, user_id):
        """Remove user from group"""
        resp, err = await self.client.remove_user_from_group(group_id, user_id)
        if err:
            raise Exception(f'Error removing user from group: {err}')
        return True

    async def get_group_members(self, group_id):
        """Get all members of a group"""
        users, resp, err = await self.client.list_group_users(group_id)
        if err:
            raise Exception(f'Error fetching group members: {err}')

        members = []
        async for user in users:
            members.append(user)

        return members


# Example usage
if __name__ == '__main__':
    async def main():
        okta = OktaClientWrapper()

        # List first 10 users
        print('Listing users...')
        users = await okta.list_users(limit=10)
        for user in users:
            print(f'  - {user.profile.email}: {user.profile.first_name} {user.profile.last_name}')

        # List groups
        print('\nListing groups...')
        groups = await okta.list_groups()
        for group in groups:
            print(f'  - {group.profile.name} ({group.id})')

    # Run async main
    asyncio.run(main())
