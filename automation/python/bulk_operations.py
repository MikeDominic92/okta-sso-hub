"""
Bulk Operations Script

Performs bulk user operations including updates, deactivations, and deletions.
"""

import asyncio
import csv
import argparse
from okta_client import OktaClientWrapper


async def bulk_update_users(okta, csv_file):
    """Bulk update users from CSV"""
    updated_count = 0

    with open(csv_file, 'r') as f:
        reader = csv.DictReader(f)

        for row in reader:
            try:
                user_id = row.get('userId') or row.get('email')
                updates = {k: v for k, v in row.items() if k not in ['userId', 'email'] and v}

                print(f'Updating user: {user_id}...')
                await okta.update_user(user_id, updates)
                print(f'✓ Updated user: {user_id}')
                updated_count += 1

            except Exception as e:
                print(f'✗ Error updating user {user_id}: {str(e)}')

    return updated_count


async def bulk_deactivate_users(okta, user_ids_file):
    """Bulk deactivate users"""
    deactivated_count = 0

    with open(user_ids_file, 'r') as f:
        for line in f:
            user_id = line.strip()
            if not user_id:
                continue

            try:
                print(f'Deactivating user: {user_id}...')
                await okta.deactivate_user(user_id)
                print(f'✓ Deactivated user: {user_id}')
                deactivated_count += 1

            except Exception as e:
                print(f'✗ Error deactivating user {user_id}: {str(e)}')

    return deactivated_count


async def export_users_to_csv(okta, output_file):
    """Export all users to CSV"""
    print('Fetching all users...')
    users = await okta.list_users()

    with open(output_file, 'w', newline='') as f:
        fieldnames = ['id', 'email', 'firstName', 'lastName', 'status', 'created', 'lastLogin']
        writer = csv.DictWriter(f, fieldnames=fieldnames)

        writer.writeheader()

        for user in users:
            writer.writerow({
                'id': user.id,
                'email': user.profile.email,
                'firstName': user.profile.first_name,
                'lastName': user.profile.last_name,
                'status': user.status,
                'created': user.created,
                'lastLogin': user.last_login
            })

    print(f'✓ Exported {len(users)} users to {output_file}')
    return len(users)


async def main():
    parser = argparse.ArgumentParser(description='Bulk operations for Okta users')
    parser.add_argument('--update', help='CSV file with user updates')
    parser.add_argument('--deactivate', help='Text file with user IDs to deactivate')
    parser.add_argument('--export', help='Export users to CSV file')

    args = parser.parse_args()

    okta = OktaClientWrapper()

    if args.update:
        count = await bulk_update_users(okta, args.update)
        print(f'\nUpdated {count} users')

    elif args.deactivate:
        count = await bulk_deactivate_users(okta, args.deactivate)
        print(f'\nDeactivated {count} users')

    elif args.export:
        count = await export_users_to_csv(okta, args.export)
        print(f'\nExported {count} users')

    else:
        print('Error: Provide --update, --deactivate, or --export')
        parser.print_help()


if __name__ == '__main__':
    asyncio.run(main())
