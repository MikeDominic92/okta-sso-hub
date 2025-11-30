# Security Best Practices

Comprehensive security guidelines for OAuth 2.0, OIDC, and SAML implementations in the Okta SSO Hub.

## Table of Contents

1. [Security Overview](#security-overview)
2. [OAuth 2.0 & OIDC Security](#oauth-20--oidc-security)
3. [SAML Security](#saml-security)
4. [Token Management](#token-management)
5. [API Security](#api-security)
6. [Network Security](#network-security)
7. [Secrets Management](#secrets-management)
8. [Common Vulnerabilities](#common-vulnerabilities)
9. [Security Checklist](#security-checklist)

## Security Overview

### Defense in Depth

This project implements multiple security layers:

1. **Authentication** - Verify user identity (password + MFA)
2. **Authorization** - Control access to resources (scopes, claims)
3. **Transport Security** - Encrypt data in transit (HTTPS/TLS)
4. **Token Security** - Protect and validate tokens (JWT signature)
5. **Session Security** - Secure session management (HttpOnly cookies)
6. **Input Validation** - Prevent injection attacks (sanitize inputs)
7. **Monitoring** - Detect and respond to threats (logging, alerts)

### Security Standards

Complies with:
- ✅ **OAuth 2.0** - RFC 6749
- ✅ **OAuth 2.0 Security Best Practices** - RFC 8252, RFC 8628
- ✅ **OpenID Connect Core** - OIDC Spec
- ✅ **SAML 2.0** - OASIS Standard
- ✅ **PKCE** - RFC 7636 (Proof Key for Code Exchange)
- ✅ **JWT** - RFC 7519 (JSON Web Tokens)
- ✅ **SCIM 2.0** - RFC 7644
- ✅ **NIST Cybersecurity Framework**

## OAuth 2.0 & OIDC Security

### Authorization Code Flow with PKCE

**Why PKCE?**
- Eliminates need for client secrets in SPAs
- Prevents authorization code interception attacks
- Binds code exchange to original requestor

**Implementation:**

```typescript
// React OIDC SPA uses PKCE automatically
const oktaAuth = new OktaAuth({
  issuer: 'https://dev-12345678.okta.com/oauth2/default',
  clientId: '0oa...',
  redirectUri: 'http://localhost:3000/login/callback',
  pkce: true,  // PKCE enabled by default in Okta SDK
  scopes: ['openid', 'profile', 'email']
});
```

**PKCE Flow:**
1. Generate random `code_verifier` (43-128 chars)
2. Create `code_challenge` = BASE64URL(SHA256(code_verifier))
3. Send `code_challenge` + method (S256) to authorization endpoint
4. Receive authorization code
5. Send `code_verifier` + code to token endpoint
6. Okta validates challenge matches verifier
7. Return tokens only if valid

### State Parameter (CSRF Protection)

**Purpose:** Prevent Cross-Site Request Forgery attacks

**How it works:**
```typescript
// Okta SDK handles state automatically
// Manual implementation:
const state = generateRandomString(32);
sessionStorage.setItem('oauth_state', state);

// Authorization request
const authUrl = `${issuer}/v1/authorize?
  client_id=${clientId}&
  response_type=code&
  scope=openid&
  redirect_uri=${redirectUri}&
  state=${state}`;

// Callback validation
const returnedState = new URLSearchParams(window.location.search).get('state');
if (returnedState !== sessionStorage.getItem('oauth_state')) {
  throw new Error('State mismatch - possible CSRF attack');
}
```

### Nonce (ID Token Validation)

**Purpose:** Prevent replay attacks on ID tokens

```typescript
// Okta SDK includes nonce automatically
const nonce = generateRandomString(32);

// Nonce sent in auth request
// Okta includes nonce claim in ID token
// SDK validates nonce matches
```

### Redirect URI Validation

**Critical Security Control:**

✅ **Do:**
- Exact match redirect URIs in Okta app configuration
- Use HTTPS in production (never HTTP)
- Avoid wildcards in redirect URIs
- Validate redirect_uri parameter matches registered URIs

❌ **Don't:**
- Use `http://` in production
- Allow open redirects
- Use query parameters in redirect URIs
- Trust redirect_uri from user input

**Example Configuration:**

```
Registered Redirect URIs:
✅ https://app.example.com/callback
✅ https://app.example.com/implicit/callback
❌ https://app.example.com/*
❌ http://app.example.com/callback (production)
✅ http://localhost:3000/login/callback (development only)
```

### Scope-Based Authorization

**Principle of Least Privilege:**

Request only necessary scopes:

```typescript
// Good - minimal scopes
scopes: ['openid', 'profile', 'email']

// Bad - excessive scopes
scopes: ['openid', 'profile', 'email', 'groups', 'address', 'phone']
```

**Custom Scopes for API:**

```typescript
// Request specific API access
scopes: ['openid', 'profile', 'read:data', 'write:data']

// API validates scopes
if (!jwt.claims.scp.includes('read:data')) {
  return res.status(403).json({ error: 'Insufficient scope' });
}
```

## SAML Security

### XML Signature Validation

**Critical:** Always validate SAML assertion signatures

```python
# Flask SAML - python3-saml handles validation
auth = init_saml_auth(request)
auth.process_response()

errors = auth.get_errors()
if errors:
    raise SecurityException(f'SAML validation failed: {errors}')

# Verify signature
if not auth.is_authenticated():
    raise SecurityException('SAML assertion signature invalid')
```

### Certificate Management

**Best Practices:**

1. **Verify IdP Certificate:**
   ```python
   # settings.json
   "idp": {
     "x509cert": "MIIDpDCCAoygAwIBAgIGAY..."  # From Okta metadata
   }
   ```

2. **Validate Certificate Chain:**
   - Ensure certificate is issued by trusted CA
   - Check certificate hasn't expired
   - Verify certificate matches Okta's current cert

3. **Certificate Rotation:**
   - Monitor Okta certificate expiration
   - Download new metadata before expiration
   - Update `settings.json` with new cert
   - Test before old cert expires

4. **SP Certificate (Optional but Recommended):**
   ```bash
   # Generate SP signing certificate
   openssl req -new -x509 -days 3652 -nodes \
     -out sp.crt -keyout sp.key

   # Add to settings.json
   "sp": {
     "x509cert": "...",
     "privateKey": "..."
   }
   ```

### Assertion Validation

**Validate ALL of these:**

1. **Signature:** Cryptographic verification
2. **Issuer:** Must match expected Okta entity ID
3. **Audience:** Must match SP entity ID
4. **NotBefore/NotOnOrAfter:** Time window validity
5. **InResponseTo:** Matches original request ID
6. **Destination:** Matches ACS URL
7. **Subject:** Contains authenticated user identifier

```python
# python3-saml validates these automatically
# Manual validation example:
assertion = auth.get_last_assertion()

if assertion.get_issuer() != expected_idp_entity_id:
    raise SecurityException('Invalid issuer')

if assertion.get_audience() != sp_entity_id:
    raise SecurityException('Invalid audience')

# Check time validity
not_before = assertion.get_not_before()
not_on_or_after = assertion.get_not_on_or_after()
now = datetime.utcnow()

if now < not_before or now >= not_on_or_after:
    raise SecurityException('Assertion expired')
```

### Replay Attack Prevention

**Store processed assertion IDs:**

```python
import redis
redis_client = redis.StrictRedis()

@app.route('/saml/acs', methods=['POST'])
def acs():
    auth = init_saml_auth(request)
    auth.process_response()

    # Get assertion ID
    response_id = auth.get_last_response_id()

    # Check if already processed
    if redis_client.get(f'saml_assertion:{response_id}'):
        raise SecurityException('Assertion replay detected')

    # Store assertion ID (expire after 5 minutes)
    redis_client.setex(f'saml_assertion:{response_id}', 300, '1')

    # Continue processing...
```

### Logout Security (Single Logout)

**Implement SLO to prevent session hijacking:**

```python
@app.route('/logout')
def logout():
    auth = init_saml_auth(request)

    # Generate SLO request
    slo_url = auth.logout(
        return_to='/',
        name_id=session.get('samlNameId'),
        session_index=session.get('samlSessionIndex')
    )

    # Clear local session
    session.clear()

    # Redirect to IdP for global logout
    return redirect(slo_url)
```

## Token Management

### Token Storage

**Security Comparison:**

| Storage | Security | Persistence | XSS Risk | Recommendation |
|---------|----------|-------------|----------|----------------|
| **Memory** | Highest | Lost on refresh | None | Production (high security) |
| **sessionStorage** | High | Lost on tab close | Low | Production (balanced) |
| **localStorage** | Medium | Persists | Medium | Development only |
| **Cookies** | High (if HttpOnly) | Configurable | Low (if HttpOnly) | Backend sessions |

**Recommended for SPAs:**

```typescript
const oktaAuth = new OktaAuth({
  // ...
  tokenManager: {
    storage: 'sessionStorage',  // Good balance
    // storage: 'memory',  // Highest security (tokens lost on refresh)
    autoRenew: true,
    expireEarlySeconds: 300  // Renew 5 minutes before expiry
  }
});
```

### Token Validation

**Always validate JWT tokens:**

```javascript
// Node.js API - Server-side validation
const OktaJwtVerifier = require('@okta/jwt-verifier');

const oktaJwtVerifier = new OktaJwtVerifier({
  issuer: 'https://dev-12345678.okta.com/oauth2/default',
  clientId: '0oa...'
});

async function verifyToken(req, res, next) {
  try {
    const authHeader = req.headers.authorization;
    if (!authHeader || !authHeader.startsWith('Bearer ')) {
      return res.status(401).json({ error: 'Missing token' });
    }

    const token = authHeader.split(' ')[1];

    // Validates:
    // 1. Signature (cryptographic verification)
    // 2. Issuer (matches expected issuer)
    // 3. Audience (matches client ID or api://default)
    // 4. Expiration (not expired)
    // 5. Not before (nbf claim)
    // 6. Issued at (iat claim)
    const jwt = await oktaJwtVerifier.verifyAccessToken(token, 'api://default');

    req.user = jwt.claims;
    next();
  } catch (error) {
    res.status(401).json({ error: 'Invalid token' });
  }
}
```

### Token Expiration

**Configure appropriate lifetimes:**

| Token Type | Recommended Lifetime | Okta Default |
|------------|---------------------|--------------|
| ID Token | 1 hour | 1 hour |
| Access Token | 1 hour | 1 hour |
| Refresh Token (SPA) | 7-90 days | 90 days |
| Refresh Token (Mobile) | 90 days | 90 days |

**Configure in Okta:**

1. Go to **Security → API → Authorization Servers → default**
2. Click **Access Policies** tab
3. Edit rule
4. Set token lifetimes:
   - Access token: 1 hour
   - Refresh token: 90 days (SPAs)

### Token Refresh

**Automatic refresh (recommended):**

```typescript
// Okta SDK handles automatically
const oktaAuth = new OktaAuth({
  tokenManager: {
    autoRenew: true,
    expireEarlySeconds: 300
  }
});

// SDK refreshes tokens 5 minutes before expiry
```

**Manual refresh (if needed):**

```typescript
try {
  const newToken = await oktaAuth.tokenManager.renew('accessToken');
  console.log('Token refreshed:', newToken);
} catch (error) {
  // Refresh failed - redirect to login
  await oktaAuth.signInWithRedirect();
}
```

### Token Revocation

**Revoke tokens on logout:**

```typescript
async function logout() {
  const accessToken = await oktaAuth.getAccessToken();
  const refreshToken = await oktaAuth.tokenManager.get('refreshToken');

  // Revoke tokens at Okta
  if (refreshToken) {
    await oktaAuth.revokeRefreshToken(refreshToken.refreshToken);
  }
  if (accessToken) {
    await oktaAuth.revokeAccessToken(accessToken);
  }

  // Clear local storage
  await oktaAuth.signOut();
}
```

## API Security

### HTTPS/TLS

**Always use HTTPS in production:**

```javascript
// Express.js - Force HTTPS
app.use((req, res, next) => {
  if (process.env.NODE_ENV === 'production' && !req.secure) {
    return res.redirect('https://' + req.headers.host + req.url);
  }
  next();
});
```

### CORS Configuration

**Restrict to specific origins:**

```javascript
const cors = require('cors');

// Good - specific origin
app.use(cors({
  origin: 'https://app.example.com',
  credentials: true
}));

// Bad - wildcard (never use in production)
app.use(cors({ origin: '*' }));  // ❌ INSECURE

// Better - multiple specific origins
const allowedOrigins = [
  'https://app.example.com',
  'https://admin.example.com'
];

app.use(cors({
  origin: (origin, callback) => {
    if (allowedOrigins.includes(origin) || !origin) {
      callback(null, true);
    } else {
      callback(new Error('Not allowed by CORS'));
    }
  },
  credentials: true
}));
```

### Security Headers

**Add security headers to all responses:**

```javascript
const helmet = require('helmet');

app.use(helmet({
  contentSecurityPolicy: {
    directives: {
      defaultSrc: ["'self'"],
      styleSrc: ["'self'", "'unsafe-inline'"],
      scriptSrc: ["'self'"],
      imgSrc: ["'self'", "data:", "https:"],
      connectSrc: ["'self'", "https://*.okta.com"]
    }
  },
  hsts: {
    maxAge: 31536000,
    includeSubDomains: true,
    preload: true
  }
}));

// Additional headers
app.use((req, res, next) => {
  res.setHeader('X-Content-Type-Options', 'nosniff');
  res.setHeader('X-Frame-Options', 'DENY');
  res.setHeader('X-XSS-Protection', '1; mode=block');
  res.setHeader('Referrer-Policy', 'strict-origin-when-cross-origin');
  next();
});
```

### Rate Limiting

**Prevent brute force attacks:**

```javascript
const rateLimit = require('express-rate-limit');

// General API rate limit
const apiLimiter = rateLimit({
  windowMs: 15 * 60 * 1000, // 15 minutes
  max: 100, // 100 requests per window
  message: 'Too many requests, please try again later'
});

app.use('/api/', apiLimiter);

// Stricter limit for auth endpoints
const authLimiter = rateLimit({
  windowMs: 15 * 60 * 1000,
  max: 5, // Only 5 attempts
  message: 'Too many login attempts, please try again later'
});

app.use('/api/auth/', authLimiter);
```

### Input Validation

**Validate and sanitize ALL inputs:**

```javascript
const { body, validationResult } = require('express-validator');

app.post('/api/users',
  // Validation rules
  body('email').isEmail().normalizeEmail(),
  body('name').trim().isLength({ min: 1, max: 100 }),
  body('age').optional().isInt({ min: 0, max: 150 }),

  // Check validation results
  (req, res) => {
    const errors = validationResult(req);
    if (!errors.isEmpty()) {
      return res.status(400).json({ errors: errors.array() });
    }

    // Process valid data
    createUser(req.body);
  }
);
```

## Network Security

### Trusted Origins

**Configure in Okta:**

1. Go to **Security → API → Trusted Origins**
2. Add production origins only
3. Never use wildcards

```
✅ Good:
- https://app.example.com (CORS + Redirect)
- https://admin.example.com (CORS + Redirect)

❌ Bad:
- http://app.example.com (HTTP in production)
- https://*.example.com (wildcard)
- * (wildcard all)
```

### IP Whitelisting (Optional)

**Restrict access by IP:**

1. Go to **Security → Networks**
2. Create network zone:
   - Name: "Office Network"
   - Gateway IPs: `203.0.113.0/24`
3. Apply to authentication policies

### DDoS Protection

**Use CDN/WAF in production:**

- Cloudflare (free tier available)
- AWS CloudFront + WAF
- Azure Front Door

## Secrets Management

### Environment Variables

**Never commit secrets to Git:**

```bash
# .env (in .gitignore)
OKTA_DOMAIN=dev-12345678.okta.com
OKTA_API_TOKEN=00abc...
OKTA_CLIENT_ID=0oa...
DATABASE_URL=postgresql://...
```

**Load secrets:**

```javascript
// Node.js
require('dotenv').config();
const apiToken = process.env.OKTA_API_TOKEN;
```

```python
# Python
from dotenv import load_dotenv
load_dotenv()
api_token = os.getenv('OKTA_API_TOKEN')
```

### Production Secrets

**Use secret managers:**

- **AWS Secrets Manager**
- **Azure Key Vault**
- **Google Secret Manager**
- **HashiCorp Vault**

```javascript
// Example: AWS Secrets Manager
const AWS = require('aws-sdk');
const secretsManager = new AWS.SecretsManager();

async function getSecret(secretName) {
  const data = await secretsManager.getSecretValue({ SecretId: secretName }).promise();
  return JSON.parse(data.SecretString);
}

const oktaCreds = await getSecret('okta/credentials');
```

### API Token Rotation

**Rotate Okta API tokens every 90 days:**

1. Create new token in Okta
2. Update environment variables
3. Deploy updated configuration
4. Verify new token works
5. Revoke old token

## Common Vulnerabilities

### Cross-Site Scripting (XSS)

**Prevention:**

```javascript
// React automatically escapes content
<div>{userInput}</div>  // Safe

// Dangerous - never use
<div dangerouslySetInnerHTML={{__html: userInput}} />  // ❌

// Server-side - sanitize HTML
const sanitizeHtml = require('sanitize-html');
const clean = sanitizeHtml(userInput);
```

### SQL Injection

**Prevention:**

```javascript
// Good - parameterized query
db.query('SELECT * FROM users WHERE email = $1', [userEmail]);

// Bad - string concatenation
db.query(`SELECT * FROM users WHERE email = '${userEmail}'`);  // ❌
```

### CSRF (Cross-Site Request Forgery)

**Prevention:**

- Use `state` parameter in OAuth (automatic in Okta SDK)
- SameSite cookies: `SameSite=Strict` or `Lax`
- CSRF tokens for form submissions

```javascript
// Express.js
const csrf = require('csurf');
app.use(csrf({ cookie: true }));
```

### Session Fixation

**Prevention:**

```python
# Flask - regenerate session ID after login
@app.route('/login', methods=['POST'])
def login():
    # Authenticate user
    user = authenticate(username, password)

    # Regenerate session ID
    session.clear()
    session['user_id'] = user.id
    session.modified = True
```

## Security Checklist

### Development

- [ ] PKCE enabled for OAuth flows
- [ ] State parameter validated
- [ ] Redirect URIs exactly match registered URIs
- [ ] Secrets in `.env` file (not committed to Git)
- [ ] `.gitignore` includes `.env`, `*.key`, `*.pem`
- [ ] SAML signature validation enabled
- [ ] JWT signature validation implemented
- [ ] Token expiration checked
- [ ] Input validation on all endpoints
- [ ] CORS restricted to specific origins
- [ ] Security headers configured
- [ ] Rate limiting implemented

### Production

- [ ] HTTPS/TLS enforced (no HTTP)
- [ ] Trusted origins configured in Okta
- [ ] Custom domain configured (optional)
- [ ] MFA enforced for all users
- [ ] Session timeout configured (max 8 hours)
- [ ] Secrets stored in secret manager
- [ ] API tokens rotated (90-day schedule)
- [ ] Security headers (CSP, HSTS, etc.)
- [ ] CDN/WAF enabled (DDoS protection)
- [ ] Monitoring and alerting configured
- [ ] Incident response plan documented
- [ ] Regular security audits scheduled

### Compliance

- [ ] Audit logging enabled
- [ ] User consent flows implemented (if required)
- [ ] Data retention policy configured
- [ ] Privacy policy published
- [ ] Terms of service accepted
- [ ] GDPR compliance (if applicable)
- [ ] SOC 2 Type II (Okta provides this)

## Monitoring & Alerts

### Okta System Log

Monitor for suspicious activity:

1. Go to **Reports → System Log**
2. Watch for:
   - Multiple failed login attempts
   - MFA challenges failed
   - User lockouts
   - API authentication failures
   - Token revocations

### Set Up Alerts

1. Go to **Reports → System Log**
2. Create alert for:
   ```
   Event: user.session.access_admin_app
   Condition: More than 5 failed attempts in 10 minutes
   Action: Email security team
   ```

### Application Monitoring

**Log security events:**

```javascript
const winston = require('winston');

const logger = winston.createLogger({
  level: 'info',
  format: winston.format.json(),
  transports: [
    new winston.transports.File({ filename: 'security.log' })
  ]
});

// Log authentication events
logger.info('Login attempt', {
  user: userEmail,
  ip: req.ip,
  success: true
});

// Log authorization failures
logger.warn('Unauthorized access attempt', {
  user: userEmail,
  resource: req.path,
  ip: req.ip
});
```

## Incident Response

### If Token Compromised

1. Revoke all tokens for affected user
2. Force password reset
3. Review audit logs for unauthorized access
4. Rotate API tokens if admin token compromised
5. Notify affected users

### If SAML Certificate Compromised

1. Generate new SP certificate
2. Update metadata in Okta
3. Revoke old certificate
4. Investigate how compromise occurred
5. Audit all SAML sessions

## References

- [OAuth 2.0 Security Best Practices](https://datatracker.ietf.org/doc/html/draft-ietf-oauth-security-topics)
- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [Okta Security Best Practices](https://developer.okta.com/docs/concepts/security-best-practices/)
- [NIST Digital Identity Guidelines](https://pages.nist.gov/800-63-3/)

---

**Security is Critical!** Follow these practices to protect user data and prevent breaches.
