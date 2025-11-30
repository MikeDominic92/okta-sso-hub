"""
Create Users Script

Creates single or bulk users in Okta.
Supports CSV import and manual user creation.
"""

import asyncio
import csv
import argparse
from okta_client import OktaClientWrapper


async def create_single_user(okta, email, first_name, last_name, mobile_phone=None):
    """Create a single user"""
    user_profile = {
        'firstName': first_name,
        'lastName': last_name,
        'email': email,
        'login': email
    }

    if mobile_phone:
        user_profile['mobilePhone'] = mobile_phone

    print(f'Creating user: {email}...')
    user = await okta.create_user(user_profile, activate=True)
    print(f'✓ Created user: {user.profile.email} (ID: {user.id})')
    return user


async def create_users_from_csv(okta, csv_file):
    """Create multiple users from CSV file"""
    created_users = []

    with open(csv_file, 'r') as f:
        reader = csv.DictReader(f)

        for row in reader:
            try:
                user = await create_single_user(
                    okta,
                    email=row['email'],
                    first_name=row['firstName'],
                    last_name=row['lastName'],
                    mobile_phone=row.get('mobilePhone')
                )
                created_users.append(user)

            except Exception as e:
                print(f'✗ Error creating user {row["email"]}: {str(e)}')

    return created_users


async def main():
    parser = argparse.ArgumentParser(description='Create users in Okta')
    parser.add_argument('--csv', help='Path to CSV file with user data')
    parser.add_argument('--email', help='User email address')
    parser.add_argument('--first-name', help='User first name')
    parser.add_argument('--last-name', help='User last name')
    parser.add_argument('--mobile', help='User mobile phone')

    args = parser.parse_args()

    okta = OktaClientWrapper()

    if args.csv:
        # Bulk creation from CSV
        print(f'Creating users from CSV: {args.csv}')
        users = await create_users_from_csv(okta, args.csv)
        print(f'\nCreated {len(users)} users successfully')

    elif args.email and args.first_name and args.last_name:
        # Single user creation
        await create_single_user(
            okta,
            email=args.email,
            first_name=args.first_name,
            last_name=args.last_name,
            mobile_phone=args.mobile
        )

    else:
        print('Error: Provide either --csv or --email, --first-name, and --last-name')
        parser.print_help()


if __name__ == '__main__':
    asyncio.run(main())
