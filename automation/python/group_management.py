"""
Group Management Script

CRUD operations for Okta groups and group membership management.
"""

import asyncio
import argparse
from okta_client import OktaClientWrapper


async def list_groups(okta, query=None):
    """List all groups"""
    groups = await okta.list_groups(query)

    print(f'Found {len(groups)} groups:')
    for group in groups:
        print(f'  - {group.profile.name} (ID: {group.id})')
        print(f'    Description: {group.profile.description or "N/A"}')

    return groups


async def create_group(okta, name, description=''):
    """Create new group"""
    print(f'Creating group: {name}...')
    group = await okta.create_group(name, description)
    print(f'✓ Created group: {group.profile.name} (ID: {group.id})')
    return group


async def add_users_to_group(okta, group_id, user_emails):
    """Add multiple users to a group"""
    added_count = 0

    for email in user_emails:
        try:
            # Find user by email
            users = await okta.list_users(query=email)
            if not users:
                print(f'✗ User not found: {email}')
                continue

            user = users[0]
            await okta.add_user_to_group(group_id, user.id)
            print(f'✓ Added {email} to group')
            added_count += 1

        except Exception as e:
            print(f'✗ Error adding {email}: {str(e)}')

    return added_count


async def list_group_members(okta, group_id):
    """List all members of a group"""
    members = await okta.get_group_members(group_id)

    print(f'Group has {len(members)} members:')
    for member in members:
        print(f'  - {member.profile.email}: {member.profile.first_name} {member.profile.last_name}')

    return members


async def main():
    parser = argparse.ArgumentParser(description='Manage Okta groups')
    parser.add_argument('--list', action='store_true', help='List all groups')
    parser.add_argument('--create', help='Create group with given name')
    parser.add_argument('--description', help='Group description (for --create)')
    parser.add_argument('--add-users', help='Group ID to add users to')
    parser.add_argument('--users', nargs='+', help='User emails to add to group')
    parser.add_argument('--members', help='List members of group ID')

    args = parser.parse_args()

    okta = OktaClientWrapper()

    if args.list:
        await list_groups(okta)

    elif args.create:
        await create_group(okta, args.create, args.description or '')

    elif args.add_users and args.users:
        count = await add_users_to_group(okta, args.add_users, args.users)
        print(f'\nAdded {count} users to group')

    elif args.members:
        await list_group_members(okta, args.members)

    else:
        print('Error: Provide --list, --create, --add-users, or --members')
        parser.print_help()


if __name__ == '__main__':
    asyncio.run(main())
