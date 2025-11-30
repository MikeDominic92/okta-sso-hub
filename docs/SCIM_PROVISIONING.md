# SCIM 2.0 Provisioning Guide

This guide explains how to set up automated user provisioning using SCIM 2.0 (System for Cross-domain Identity Management).

## Table of Contents

1. [SCIM Overview](#scim-overview)
2. [Build SCIM Server](#build-scim-server)
3. [Configure SCIM App in Okta](#configure-scim-app-in-okta)
4. [Test Provisioning](#test-provisioning)
5. [Deprovisioning](#deprovisioning)
6. [Group Sync](#group-sync)
7. [Troubleshooting](#troubleshooting)

## SCIM Overview

### What is SCIM?

**SCIM (System for Cross-domain Identity Management)** is a REST API standard for automating user provisioning between systems.

**Benefits:**
- Automated user creation/updates/deletion
- Group membership synchronization
- Reduced manual administration
- Faster onboarding/offboarding
- Consistent identity data across systems

### SCIM Flow

```
Okta (SCIM Client) → SCIM Server (Your App) → Database

Create User in Okta → SCIM POST /Users → User created in app
Update User in Okta → SCIM PUT /Users/{id} → User updated in app
Delete User in Okta → SCIM DELETE /Users/{id} → User deactivated in app
Assign to Group → SCIM PATCH /Users/{id} → Group membership updated
```

### SCIM 2.0 Endpoints

| Method | Endpoint | Purpose |
|--------|----------|---------|
| GET | /scim/v2/Users | List users |
| GET | /scim/v2/Users/{id} | Get user details |
| POST | /scim/v2/Users | Create user |
| PUT | /scim/v2/Users/{id} | Update user (full) |
| PATCH | /scim/v2/Users/{id} | Update user (partial) |
| DELETE | /scim/v2/Users/{id} | Delete/deactivate user |
| GET | /scim/v2/Groups | List groups |
| GET | /scim/v2/Groups/{id} | Get group details |
| POST | /scim/v2/Groups | Create group |
| PATCH | /scim/v2/Groups/{id} | Update group members |

## Build SCIM Server

### Step 1: Install Dependencies

```bash
cd scim
pip install -r requirements.txt
```

This installs:
- `flask` - Web framework
- `flask-cors` - CORS support
- `scim2-filter-parser` - SCIM filter parsing
- `python-dotenv` - Environment variables

### Step 2: Configure Environment

Create `scim/.env`:

```bash
SCIM_BASE_URL=http://localhost:5001/scim/v2
SCIM_BEARER_TOKEN=your_secure_token_here_use_openssl_rand_hex_32
DATABASE_PATH=scim_users.db
```

Generate secure token:
```bash
openssl rand -hex 32
# Output: a1b2c3d4e5f6...
```

### Step 3: Run SCIM Server

```bash
python scim_server.py
```

Output:
```
 * Running on http://localhost:5001
 * SCIM endpoints available at /scim/v2/
```

### Step 4: Test SCIM Server

Verify endpoints are working:

```bash
# Test with bearer token
curl -X GET "http://localhost:5001/scim/v2/Users" \
  -H "Authorization: Bearer your_secure_token_here" \
  -H "Content-Type: application/scim+json"
```

Expected response:
```json
{
  "schemas": ["urn:ietf:params:scim:api:messages:2.0:ListResponse"],
  "totalResults": 0,
  "startIndex": 1,
  "itemsPerPage": 100,
  "Resources": []
}
```

## Configure SCIM App in Okta

### Step 1: Create SCIM Application

1. Log in to Okta Admin Console
2. Go to **Applications → Applications**
3. Click **Browse App Catalog**
4. Search for **SCIM 2.0 Test App (Header Auth)**
5. Click **Add Integration**
6. Click **Done**

Alternatively, create custom SCIM app:

1. Click **Create App Integration**
2. Select **SWA - Secure Web Authentication**
3. Click **Next**
4. Configure basic settings
5. Click **Done**

### Step 2: Enable SCIM Provisioning

1. Open the created application
2. Go to **Provisioning** tab
3. Click **Configure API Integration**
4. Check **Enable API integration**
5. Configure:
   - **SCIM Base URL:** `http://localhost:5001/scim/v2`
   - **Unique identifier field for users:** `userName`
   - **Supported provisioning actions:**
     - ✅ Push New Users
     - ✅ Push Profile Updates
     - ✅ Push Groups
   - **Authentication Mode:** HTTP Header
   - **Authorization:** `Bearer your_secure_token_here`
6. Click **Test API Credentials**

Expected result: ✅ **Success**

7. Click **Save**

### Step 3: Configure Provisioning Settings

Go to **Provisioning → To App** tab:

#### Create Users
- ✅ Enable **Create Users**
- Verify attribute mapping

#### Update User Attributes
- ✅ Enable **Update User Attributes**
- Attributes to sync:
  - Given name
  - Family name
  - Email
  - Username

#### Deactivate Users
- ✅ Enable **Deactivate Users**
- Action: Set `active` to `false` (don't delete)

Click **Save**

### Step 4: Attribute Mapping

Go to **Provisioning → To App → Attribute Mappings**

Default mappings:

| Okta Attribute | SCIM Attribute | Transform |
|----------------|----------------|-----------|
| user.firstName | name.givenName | - |
| user.lastName | name.familyName | - |
| user.email | emails[0].value | - |
| user.login | userName | - |
| user.secondEmail | emails[1].value | - |

Add custom mappings if needed:

1. Click **Add Mapping**
2. Configure:
   - **Okta field:** user.department
   - **App field:** department
3. Click **Save Mappings**

## Test Provisioning

### Step 1: Assign User to SCIM App

1. Go to **Applications → SCIM App → Assignments**
2. Click **Assign → Assign to People**
3. Select test user (e.g., john.developer@example.com)
4. Click **Assign**
5. Review attribute values
6. Click **Save and Go Back**
7. Click **Done**

### Step 2: Verify User Created

Check SCIM server logs:
```
POST /scim/v2/Users
{
  "schemas": ["urn:ietf:params:scim:schemas:core:2.0:User"],
  "userName": "john.developer@example.com",
  "name": {
    "givenName": "John",
    "familyName": "Developer"
  },
  "emails": [{
    "value": "john.developer@example.com",
    "primary": true
  }],
  "active": true
}

Response: 201 Created
```

Query SCIM server:
```bash
curl -X GET "http://localhost:5001/scim/v2/Users" \
  -H "Authorization: Bearer your_token"
```

Response:
```json
{
  "schemas": ["urn:ietf:params:scim:api:messages:2.0:ListResponse"],
  "totalResults": 1,
  "Resources": [{
    "id": "1",
    "userName": "john.developer@example.com",
    "name": {
      "givenName": "John",
      "familyName": "Developer"
    },
    "emails": [{
      "value": "john.developer@example.com",
      "primary": true
    }],
    "active": true
  }]
}
```

### Step 3: Update User in Okta

1. Go to **Directory → People**
2. Select user: john.developer@example.com
3. Click **Profile**
4. Edit **Department:** Change to "Engineering"
5. Click **Save**

Verify SCIM update:
```
PUT /scim/v2/Users/1
{
  "schemas": ["urn:ietf:params:scim:schemas:core:2.0:User"],
  "userName": "john.developer@example.com",
  "name": {
    "givenName": "John",
    "familyName": "Developer"
  },
  "department": "Engineering",
  ...
}

Response: 200 OK
```

### Step 4: Push Groups

1. Go to **Applications → SCIM App → Provisioning → To App**
2. Scroll to **Group Push**
3. Click **Push Groups → Find groups by name**
4. Search for group: "Developers"
5. Click **Save**

SCIM creates group:
```
POST /scim/v2/Groups
{
  "schemas": ["urn:ietf:params:scim:schemas:core:2.0:Group"],
  "displayName": "Developers",
  "members": [{
    "value": "1",
    "display": "john.developer@example.com"
  }]
}

Response: 201 Created
```

## Deprovisioning

### Automatic Deprovisioning

When user is unassigned from SCIM app:

1. Go to **Applications → SCIM App → Assignments**
2. Find user: john.developer@example.com
3. Click **X** (unassign)
4. Confirm removal

SCIM deactivates user:
```
PATCH /scim/v2/Users/1
{
  "schemas": ["urn:ietf:params:scim:api:messages:2.0:PatchOp"],
  "Operations": [{
    "op": "replace",
    "path": "active",
    "value": false
  }]
}

Response: 200 OK
```

User record remains in database with `active: false`.

### Hard Delete (Optional)

Configure to delete instead of deactivate:

1. Go to **Provisioning → To App**
2. Under **Deactivate Users**, change to:
   - Action: **Delete user from application**
3. Save

SCIM deletes user:
```
DELETE /scim/v2/Users/1

Response: 204 No Content
```

## Group Sync

### Create Group in Okta

1. Go to **Directory → Groups**
2. Click **Add Group**
3. Configure:
   - **Name:** QA Team
   - **Description:** Quality Assurance team members
4. Click **Save**

### Add Members

1. Click **Assign People**
2. Select users
3. Click **Save**

### Push Group to SCIM App

1. Go to **Applications → SCIM App → Provisioning → To App**
2. Scroll to **Group Push**
3. Click **Push Groups → Find groups by name**
4. Search: "QA Team"
5. Click **Save**

SCIM creates group:
```
POST /scim/v2/Groups
{
  "schemas": ["urn:ietf:params:scim:schemas:core:2.0:Group"],
  "displayName": "QA Team",
  "members": [
    {"value": "1", "display": "john.developer@example.com"},
    {"value": "2", "display": "jane.admin@example.com"}
  ]
}
```

### Update Group Membership

Add user to group in Okta:

1. Go to **Directory → Groups → QA Team**
2. Click **Assign People**
3. Select new user
4. Click **Save**

SCIM updates group:
```
PATCH /scim/v2/Groups/1
{
  "schemas": ["urn:ietf:params:scim:api:messages:2.0:PatchOp"],
  "Operations": [{
    "op": "add",
    "path": "members",
    "value": [{
      "value": "3",
      "display": "bob.user@example.com"
    }]
  }]
}
```

## SCIM Filtering

Okta sends filters to query users:

### Filter by Username

```
GET /scim/v2/Users?filter=userName eq "john.developer@example.com"
```

### Filter by Email

```
GET /scim/v2/Users?filter=emails.value eq "john@example.com"
```

### Filter by Active Status

```
GET /scim/v2/Users?filter=active eq true
```

### Pagination

```
GET /scim/v2/Users?startIndex=1&count=10
```

## Troubleshooting

### Authentication Failed

**Problem:** `401 Unauthorized`
**Solution:**
- Verify bearer token matches between Okta and SCIM server
- Check Authorization header format: `Bearer <token>`
- Regenerate token if compromised

### User Not Created

**Problem:** Provisioning task failed
**Solution:**
- Check SCIM server logs for errors
- Verify required fields are mapped (userName, emails)
- Test SCIM endpoint manually with curl
- Review Okta provisioning task details

### Attribute Not Syncing

**Problem:** Custom attribute not appearing
**Solution:**
- Verify attribute mapping in **Provisioning → To App → Mappings**
- Check SCIM server supports custom attributes
- Ensure attribute exists in Okta user profile
- Test with SCIM API directly

### Group Push Failed

**Problem:** Group not created in SCIM app
**Solution:**
- Verify Groups endpoint is implemented
- Check group members are assigned to SCIM app
- Review SCIM server logs
- Test Groups endpoint manually

### Deprovisioning Not Working

**Problem:** User still active after unassignment
**Solution:**
- Verify **Deactivate Users** is enabled
- Check SCIM server handles PATCH active=false
- Review deprovisioning action configuration
- Check SCIM server database

## Production Considerations

### HTTPS Required

Okta requires HTTPS for production SCIM endpoints:

```bash
SCIM_BASE_URL=https://yourdomain.com/scim/v2
```

### Authentication

Use secure token management:
- Store tokens in secure vault (AWS Secrets Manager, etc.)
- Rotate tokens regularly
- Use different tokens per environment
- Implement IP whitelisting

### Rate Limiting

Implement rate limiting to prevent abuse:

```python
from flask_limiter import Limiter

limiter = Limiter(
    app,
    key_func=lambda: request.headers.get('Authorization'),
    default_limits=["100 per minute"]
)

@app.route('/scim/v2/Users', methods=['GET'])
@limiter.limit("50 per minute")
def list_users():
    # ...
```

### Logging

Log all SCIM operations for audit:

```python
import logging

logging.basicConfig(
    filename='scim_audit.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

@app.route('/scim/v2/Users', methods=['POST'])
def create_user():
    logging.info(f"SCIM CREATE: {request.json}")
    # ...
```

### Error Handling

Return proper SCIM error responses:

```python
@app.errorhandler(404)
def not_found(error):
    return jsonify({
        "schemas": ["urn:ietf:params:scim:api:messages:2.0:Error"],
        "status": "404",
        "detail": "User not found"
    }), 404
```

## Next Steps

- [Configure MFA Policies](MFA_POLICIES.md)
- [Review Security Best Practices](SECURITY.md)
- [Explore Python Automation](../automation/python/README.md)

## References

- [SCIM 2.0 RFC 7644](https://datatracker.ietf.org/doc/html/rfc7644)
- [Okta SCIM Documentation](https://developer.okta.com/docs/concepts/scim/)
- [SCIM 2.0 Test App](https://saml-doc.okta.com/SCIM_Docs/index.html)

---

**SCIM Provisioning Complete!** Users now sync automatically between Okta and your app.
