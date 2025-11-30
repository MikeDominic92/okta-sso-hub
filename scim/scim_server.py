"""
SCIM 2.0 Server

Implements SCIM 2.0 protocol for automated user provisioning from Okta.
Supports users and groups endpoints with full CRUD operations.
"""

import os
import json
import sqlite3
from datetime import datetime
from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
CORS(app)

# Configuration
SCIM_BEARER_TOKEN = os.getenv('SCIM_BEARER_TOKEN', 'change_this_token')
DATABASE_PATH = os.getenv('DATABASE_PATH', 'scim_users.db')

# Initialize database
def init_db():
    conn = sqlite3.connect(DATABASE_PATH)
    c = conn.cursor()

    c.execute('''CREATE TABLE IF NOT EXISTS users
                 (id TEXT PRIMARY KEY,
                  username TEXT UNIQUE,
                  given_name TEXT,
                  family_name TEXT,
                  email TEXT,
                  active INTEGER,
                  created TEXT,
                  modified TEXT)''')

    c.execute('''CREATE TABLE IF NOT EXISTS groups
                 (id TEXT PRIMARY KEY,
                  display_name TEXT,
                  members TEXT,
                  created TEXT,
                  modified TEXT)''')

    conn.commit()
    conn.close()

init_db()

# Authentication middleware
def require_auth(f):
    def wrapper(*args, **kwargs):
        auth_header = request.headers.get('Authorization')

        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({
                'schemas': ['urn:ietf:params:scim:api:messages:2.0:Error'],
                'status': '401',
                'detail': 'Unauthorized'
            }), 401

        token = auth_header.split(' ')[1]

        if token != SCIM_BEARER_TOKEN:
            return jsonify({
                'schemas': ['urn:ietf:params:scim:api:messages:2.0:Error'],
                'status': '401',
                'detail': 'Invalid token'
            }), 401

        return f(*args, **kwargs)

    wrapper.__name__ = f.__name__
    return wrapper

# Users endpoints
@app.route('/scim/v2/Users', methods=['GET'])
@require_auth
def list_users():
    """List all users"""
    conn = sqlite3.connect(DATABASE_PATH)
    c = conn.cursor()
    c.execute('SELECT * FROM users')
    rows = c.fetchall()
    conn.close()

    resources = []
    for row in rows:
        resources.append({
            'id': row[0],
            'userName': row[1],
            'name': {
                'givenName': row[2],
                'familyName': row[3]
            },
            'emails': [{'value': row[4], 'primary': True}],
            'active': bool(row[5]),
            'meta': {
                'resourceType': 'User',
                'created': row[6],
                'lastModified': row[7]
            }
        })

    return jsonify({
        'schemas': ['urn:ietf:params:scim:api:messages:2.0:ListResponse'],
        'totalResults': len(resources),
        'startIndex': 1,
        'itemsPerPage': len(resources),
        'Resources': resources
    })

@app.route('/scim/v2/Users/<user_id>', methods=['GET'])
@require_auth
def get_user(user_id):
    """Get user by ID"""
    conn = sqlite3.connect(DATABASE_PATH)
    c = conn.cursor()
    c.execute('SELECT * FROM users WHERE id=?', (user_id,))
    row = c.fetchone()
    conn.close()

    if not row:
        return jsonify({
            'schemas': ['urn:ietf:params:scim:api:messages:2.0:Error'],
            'status': '404',
            'detail': 'User not found'
        }), 404

    return jsonify({
        'schemas': ['urn:ietf:params:scim:schemas:core:2.0:User'],
        'id': row[0],
        'userName': row[1],
        'name': {
            'givenName': row[2],
            'familyName': row[3]
        },
        'emails': [{'value': row[4], 'primary': True}],
        'active': bool(row[5]),
        'meta': {
            'resourceType': 'User',
            'created': row[6],
            'lastModified': row[7]
        }
    })

@app.route('/scim/v2/Users', methods=['POST'])
@require_auth
def create_user():
    """Create new user"""
    data = request.json
    user_id = str(hash(data['userName']))[:10]
    now = datetime.utcnow().isoformat() + 'Z'

    conn = sqlite3.connect(DATABASE_PATH)
    c = conn.cursor()

    try:
        c.execute('''INSERT INTO users VALUES (?, ?, ?, ?, ?, ?, ?, ?)''',
                  (user_id,
                   data['userName'],
                   data.get('name', {}).get('givenName', ''),
                   data.get('name', {}).get('familyName', ''),
                   data.get('emails', [{}])[0].get('value', ''),
                   1 if data.get('active', True) else 0,
                   now,
                   now))
        conn.commit()
    except sqlite3.IntegrityError:
        conn.close()
        return jsonify({
            'schemas': ['urn:ietf:params:scim:api:messages:2.0:Error'],
            'status': '409',
            'detail': 'User already exists'
        }), 409

    conn.close()

    return jsonify({
        'schemas': ['urn:ietf:params:scim:schemas:core:2.0:User'],
        'id': user_id,
        'userName': data['userName'],
        'name': data.get('name', {}),
        'emails': data.get('emails', []),
        'active': data.get('active', True),
        'meta': {
            'resourceType': 'User',
            'created': now,
            'lastModified': now
        }
    }), 201

@app.route('/scim/v2/Users/<user_id>', methods=['PUT', 'PATCH'])
@require_auth
def update_user(user_id):
    """Update user"""
    data = request.json
    now = datetime.utcnow().isoformat() + 'Z'

    conn = sqlite3.connect(DATABASE_PATH)
    c = conn.cursor()

    if request.method == 'PATCH':
        # Handle PATCH operations
        operations = data.get('Operations', [])
        for op in operations:
            if op['op'] == 'replace' and op['path'] == 'active':
                c.execute('UPDATE users SET active=?, modified=? WHERE id=?',
                          (1 if op['value'] else 0, now, user_id))
    else:
        # Handle PUT (full update)
        c.execute('''UPDATE users SET username=?, given_name=?, family_name=?,
                     email=?, active=?, modified=? WHERE id=?''',
                  (data['userName'],
                   data.get('name', {}).get('givenName', ''),
                   data.get('name', {}).get('familyName', ''),
                   data.get('emails', [{}])[0].get('value', ''),
                   1 if data.get('active', True) else 0,
                   now,
                   user_id))

    conn.commit()
    conn.close()

    return jsonify({
        'schemas': ['urn:ietf:params:scim:schemas:core:2.0:User'],
        'id': user_id,
        'meta': {'lastModified': now}
    })

@app.route('/scim/v2/Users/<user_id>', methods=['DELETE'])
@require_auth
def delete_user(user_id):
    """Delete user"""
    conn = sqlite3.connect(DATABASE_PATH)
    c = conn.cursor()
    c.execute('DELETE FROM users WHERE id=?', (user_id,))
    conn.commit()
    conn.close()

    return '', 204

# Groups endpoints
@app.route('/scim/v2/Groups', methods=['GET'])
@require_auth
def list_groups():
    """List all groups"""
    conn = sqlite3.connect(DATABASE_PATH)
    c = conn.cursor()
    c.execute('SELECT * FROM groups')
    rows = c.fetchall()
    conn.close()

    resources = []
    for row in rows:
        members = json.loads(row[2]) if row[2] else []
        resources.append({
            'id': row[0],
            'displayName': row[1],
            'members': members,
            'meta': {
                'resourceType': 'Group',
                'created': row[3],
                'lastModified': row[4]
            }
        })

    return jsonify({
        'schemas': ['urn:ietf:params:scim:api:messages:2.0:ListResponse'],
        'totalResults': len(resources),
        'Resources': resources
    })

@app.route('/scim/v2/Groups', methods=['POST'])
@require_auth
def create_group():
    """Create new group"""
    data = request.json
    group_id = str(hash(data['displayName']))[:10]
    now = datetime.utcnow().isoformat() + 'Z'

    members = json.dumps(data.get('members', []))

    conn = sqlite3.connect(DATABASE_PATH)
    c = conn.cursor()
    c.execute('INSERT INTO groups VALUES (?, ?, ?, ?, ?)',
              (group_id, data['displayName'], members, now, now))
    conn.commit()
    conn.close()

    return jsonify({
        'schemas': ['urn:ietf:params:scim:schemas:core:2.0:Group'],
        'id': group_id,
        'displayName': data['displayName'],
        'members': data.get('members', []),
        'meta': {'created': now, 'lastModified': now}
    }), 201

# Health check
@app.route('/health', methods=['GET'])
def health():
    return jsonify({'status': 'healthy', 'timestamp': datetime.utcnow().isoformat()})

if __name__ == '__main__':
    print('Starting SCIM 2.0 Server...')
    print(f'Bearer Token: {SCIM_BEARER_TOKEN}')
    print(f'Database: {DATABASE_PATH}')
    app.run(debug=True, host='0.0.0.0', port=5001)
