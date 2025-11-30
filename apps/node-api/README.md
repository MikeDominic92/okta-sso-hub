# Node.js Protected API

RESTful API with Okta JWT token verification and scope-based authorization.

## Features

- **JWT Verification** - Cryptographic validation of Okta access tokens
- **Scope-Based Authorization** - Fine-grained access control
- **Claims Validation** - Custom authorization logic based on token claims
- **CORS Support** - Secure cross-origin requests
- **Rate Limiting** - Prevent abuse and DoS attacks
- **Security Headers** - Helmet.js for HTTP security
- **Error Handling** - Comprehensive error responses

## Prerequisites

- Node.js 18.x or higher
- npm
- Okta Developer Account
- OIDC application configured in Okta

## Setup

### 1. Install Dependencies

```bash
npm install
```

### 2. Configure Environment Variables

Copy `.env.example` to `.env`:

```bash
cp .env.example .env
```

Edit `.env`:

```bash
OKTA_ISSUER=https://dev-12345678.okta.com/oauth2/default
OKTA_CLIENT_ID=0oa1b2c3d4e5f6g7h8i9
OKTA_AUDIENCE=api://default
PORT=8080
ALLOWED_ORIGINS=http://localhost:3000
```

## Running the Application

### Development Mode

```bash
npm start
```

With auto-restart on changes:

```bash
npm run dev
```

Server runs on: `http://localhost:8080`

## API Endpoints

### Public Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | API information |
| `/health` | GET | Health check |

### Protected Endpoints (Require JWT)

| Endpoint | Method | Description | Authorization |
|----------|--------|-------------|---------------|
| `/api/protected` | GET | Basic protected resource | Valid JWT |
| `/api/userinfo` | GET | User information from token | Valid JWT |
| `/api/scope-test` | GET | Scope-based auth test | Requires `profile` scope |
| `/api/admin` | GET | Admin-only endpoint | Requires `Administrators` group |
| `/api/token-info` | GET | JWT token details | Valid JWT |
| `/api/data` | GET | Sample data endpoint | Valid JWT |
| `/api/echo` | POST | Echo POST data | Valid JWT |

## Usage

### Calling Protected Endpoints

#### From React SPA

```javascript
const { authState } = useOktaAuth();
const accessToken = authState?.accessToken?.accessToken;

const response = await fetch('http://localhost:8080/api/protected', {
  headers: {
    'Authorization': `Bearer ${accessToken}`,
    'Content-Type': 'application/json'
  }
});

const data = await response.json();
```

#### Using curl

```bash
# Get access token from Okta
TOKEN="your_access_token_here"

# Call protected endpoint
curl -H "Authorization: Bearer $TOKEN" \
  http://localhost:8080/api/protected
```

#### Using Postman

1. Set Authorization type to **Bearer Token**
2. Paste access token
3. Send request

## Authentication Flow

```
Client → API (with Bearer token)
         ↓
    JWT Verification Middleware
         ↓
    Validate signature (Okta public key)
    Validate issuer
    Validate audience
    Check expiration
         ↓
    Attach claims to req.user
         ↓
    Route Handler
         ↓
    Response
```

## JWT Validation

The middleware validates:

1. **Signature** - Cryptographic verification using Okta's public key
2. **Issuer (iss)** - Matches `OKTA_ISSUER`
3. **Audience (aud)** - Matches `OKTA_AUDIENCE`
4. **Client ID (cid)** - Matches `OKTA_CLIENT_ID`
5. **Expiration (exp)** - Token not expired
6. **Not Before (nbf)** - Token is valid to use

## Scope-Based Authorization

### Example: Require Specific Scope

```javascript
const { requireScope } = require('./middleware/oktaJwtVerifier');

router.get('/api/write-data',
  requireScope('write:data'),
  (req, res) => {
    res.json({ message: 'Write access granted' });
  }
);
```

### Example: Require Multiple Scopes

```javascript
router.get('/api/sensitive',
  requireScope(['admin', 'sensitive:read']),
  (req, res) => {
    res.json({ message: 'Sensitive data access granted' });
  }
);
```

## Claims-Based Authorization

### Example: Check User Group

```javascript
router.get('/api/admin', (req, res) => {
  const userGroups = req.user.groups || [];

  if (!userGroups.includes('Administrators')) {
    return res.status(403).json({ error: 'Admin access required' });
  }

  res.json({ message: 'Admin access granted' });
});
```

### Example: Custom Claims

```javascript
const { requireClaims } = require('./middleware/oktaJwtVerifier');

router.get('/api/premium',
  requireClaims({ subscription: 'premium' }),
  (req, res) => {
    res.json({ message: 'Premium feature accessed' });
  }
);
```

## Security

### CORS Configuration

Restrict origins in `.env`:

```bash
ALLOWED_ORIGINS=https://app.example.com,https://admin.example.com
```

### Rate Limiting

Default: 100 requests per 15 minutes per IP

Adjust in `server.js`:

```javascript
const limiter = rateLimit({
  windowMs: 15 * 60 * 1000,
  max: 100
});
```

### Security Headers

Helmet.js adds:
- `X-Content-Type-Options: nosniff`
- `X-Frame-Options: SAMEORIGIN`
- `X-XSS-Protection: 1; mode=block`
- `Strict-Transport-Security` (HTTPS only)

### HTTPS in Production

Always use HTTPS:

```javascript
if (process.env.NODE_ENV === 'production' && !req.secure) {
  return res.redirect('https://' + req.headers.host + req.url);
}
```

## Error Handling

### 401 Unauthorized

```json
{
  "error": "Unauthorized",
  "message": "Invalid or expired token",
  "timestamp": "2025-11-30T12:00:00.000Z"
}
```

### 403 Forbidden

```json
{
  "error": "Forbidden",
  "message": "Insufficient scope to access this resource",
  "requiredScopes": ["write:data"],
  "userScopes": ["read:data"]
}
```

### 404 Not Found

```json
{
  "error": "Not Found",
  "message": "Route GET /api/unknown not found",
  "timestamp": "2025-11-30T12:00:00.000Z"
}
```

## Testing

### Health Check

```bash
curl http://localhost:8080/health
```

### Protected Endpoint (should fail without token)

```bash
curl http://localhost:8080/api/protected
# Returns: 401 Unauthorized
```

### With Valid Token

```bash
curl -H "Authorization: Bearer <token>" \
  http://localhost:8080/api/protected
# Returns: 200 OK with user data
```

## Production Deployment

### Environment Variables

```bash
NODE_ENV=production
PORT=8080
OKTA_ISSUER=https://yourdomain.okta.com/oauth2/default
OKTA_CLIENT_ID=0oa...
OKTA_AUDIENCE=api://default
ALLOWED_ORIGINS=https://yourdomain.com
```

### Process Manager

Use PM2 for production:

```bash
npm install -g pm2
pm2 start server.js --name okta-api
pm2 save
pm2 startup
```

### Reverse Proxy

Use Nginx for HTTPS termination and load balancing.

## Documentation

- [OIDC Integration Guide](../../docs/OIDC_INTEGRATION.md)
- [Security Best Practices](../../docs/SECURITY.md)
- [@okta/jwt-verifier Documentation](https://github.com/okta/okta-oidc-js/tree/master/packages/jwt-verifier)

---

**Built with:** Node.js • Express • @okta/jwt-verifier • OAuth 2.0
