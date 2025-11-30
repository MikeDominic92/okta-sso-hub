# React OIDC SPA

Modern single-page application (SPA) with OpenID Connect (OIDC) authentication using Okta.

## Features

- **Authorization Code Flow with PKCE** - Secure OAuth 2.0 flow for SPAs
- **Automatic Token Refresh** - Tokens renewed before expiration
- **Protected Routes** - SecureRoute component for authenticated pages
- **User Profile Display** - Show user information from Okta
- **API Integration** - Call protected APIs with access tokens
- **TypeScript** - Type-safe React development
- **Modern UI** - Clean, responsive design

## Prerequisites

- Node.js 18.x or higher
- npm or yarn
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

Edit `.env` with your Okta credentials:

```bash
REACT_APP_OKTA_DOMAIN=dev-12345678.okta.com
REACT_APP_OKTA_CLIENT_ID=0oa1b2c3d4e5f6g7h8i9
REACT_APP_OKTA_ISSUER=https://dev-12345678.okta.com/oauth2/default
REACT_APP_REDIRECT_URI=http://localhost:3000/login/callback
REACT_APP_SCOPES=openid profile email
REACT_APP_API_URL=http://localhost:8080
```

### 3. Create OIDC App in Okta

1. Log in to Okta Admin Console
2. Go to **Applications → Applications**
3. Click **Create App Integration**
4. Select:
   - **Sign-in method:** OIDC - OpenID Connect
   - **Application type:** Single-Page Application
5. Configure:
   - **App integration name:** React OIDC SPA
   - **Grant type:** Authorization Code, Refresh Token
   - **Sign-in redirect URIs:** `http://localhost:3000/login/callback`
   - **Sign-out redirect URIs:** `http://localhost:3000`
6. Click **Save**
7. Copy **Client ID** to `.env` file

### 4. Add Trusted Origin

1. Go to **Security → API → Trusted Origins**
2. Click **Add Origin**
3. Configure:
   - **Name:** React SPA Localhost
   - **Origin URL:** `http://localhost:3000`
   - **Type:** CORS, Redirect
4. Click **Save**

## Running the Application

### Development Mode

```bash
npm start
```

Application runs on: `http://localhost:3000`

Browser will automatically open and hot-reload on changes.

### Production Build

```bash
npm run build
```

Optimized production build created in `build/` directory.

### Run Tests

```bash
npm test
```

## Usage

### Login Flow

1. Navigate to `http://localhost:3000`
2. Click **Login with Okta**
3. Redirected to Okta login page
4. Enter credentials and complete MFA
5. Redirected back to Dashboard

### Dashboard Features

- **User Information** - View profile data from ID token
- **Protected API** - Test calling backend with access token
- **Token Viewer** - Inspect ID and access tokens
- **Logout** - End session and revoke tokens

## Project Structure

```
react-oidc-spa/
├── public/
│   └── index.html           # HTML template
├── src/
│   ├── index.tsx            # Application entry point
│   ├── App.tsx              # Main app component with routing
│   ├── OktaAuth.tsx         # Okta Auth SDK initialization
│   ├── config.ts            # Configuration and env variables
│   ├── Login.tsx            # Login page component
│   ├── Dashboard.tsx        # Protected dashboard component
│   ├── SecureRoute.tsx      # Protected route wrapper
│   └── reportWebVitals.ts   # Performance monitoring
├── package.json             # Dependencies and scripts
├── tsconfig.json            # TypeScript configuration
└── .env.example             # Environment variables template
```

## Code Examples

### Okta Authentication Setup

```typescript
import { OktaAuth } from '@okta/okta-auth-js';

const oktaAuth = new OktaAuth({
  issuer: 'https://dev-12345678.okta.com/oauth2/default',
  clientId: '0oa...',
  redirectUri: 'http://localhost:3000/login/callback',
  scopes: ['openid', 'profile', 'email'],
  pkce: true,
  tokenManager: {
    autoRenew: true,
    storage: 'sessionStorage'
  }
});
```

### Protected Route Component

```typescript
import { SecureRoute } from './SecureRoute';
import Dashboard from './Dashboard';

<Route path="/dashboard" element={
  <SecureRoute>
    <Dashboard />
  </SecureRoute>
} />
```

### Calling Protected API

```typescript
const { authState } = useOktaAuth();
const accessToken = authState?.accessToken?.accessToken;

const response = await fetch('http://localhost:8080/api/protected', {
  headers: {
    'Authorization': `Bearer ${accessToken}`
  }
});
```

### User Information

```typescript
import { useOktaAuth } from '@okta/okta-react';

const { oktaAuth } = useOktaAuth();
const user = await oktaAuth.getUser();

console.log(user.name);  // "John Developer"
console.log(user.email); // "john.developer@example.com"
```

## Security

### PKCE (Proof Key for Code Exchange)

This app uses PKCE to secure the authorization code flow:

1. Generate random `code_verifier`
2. Create `code_challenge` = SHA256(code_verifier)
3. Send challenge to authorization endpoint
4. Okta validates verifier matches challenge

Benefits:
- No client secret required
- Prevents authorization code interception
- Mobile and SPA safe

### Token Storage

Tokens stored in **sessionStorage** by default:
- Cleared when tab/browser closes
- Not accessible across different tabs
- Lower XSS risk than localStorage

For highest security, use `storage: 'memory'` (tokens lost on page refresh).

### HTTPS in Production

Always use HTTPS in production:
- Update redirect URIs to `https://`
- Configure SSL certificate
- Enable secure cookies

## Troubleshooting

### Issue: Redirect URI Mismatch

**Error:** `redirect_uri_mismatch`

**Solution:**
- Verify redirect URI in Okta app matches exactly
- Check for trailing slashes
- Ensure protocol matches (http vs https)

### Issue: CORS Errors

**Error:** `No 'Access-Control-Allow-Origin' header`

**Solution:**
- Add Trusted Origin in Okta for `http://localhost:3000`
- Check both CORS and Redirect are enabled
- Clear browser cache

### Issue: Token Expired

**Error:** `JWT is expired`

**Solution:**
- Enable `autoRenew: true` in tokenManager
- Check system clock is synchronized
- Verify token lifetime in Okta authorization server

### Issue: Login Loop

**Problem:** Infinite redirect loop

**Solution:**
- Check callback route is configured: `/login/callback`
- Verify SecureRoute wraps protected components
- Clear browser cookies and storage

## Production Deployment

### Environment Variables

Create `.env.production`:

```bash
REACT_APP_OKTA_DOMAIN=yourdomain.okta.com
REACT_APP_OKTA_CLIENT_ID=0oa...
REACT_APP_OKTA_ISSUER=https://yourdomain.okta.com/oauth2/default
REACT_APP_REDIRECT_URI=https://yourdomain.com/login/callback
REACT_APP_SCOPES=openid profile email
REACT_APP_API_URL=https://api.yourdomain.com
```

### Build and Deploy

```bash
# Build production bundle
npm run build

# Deploy to static hosting
# - Vercel: vercel deploy
# - Netlify: netlify deploy
# - AWS S3: aws s3 sync build/ s3://bucket-name
```

### Update Okta Configuration

1. Add production redirect URIs in Okta app
2. Add production trusted origin
3. Update sign-out redirect URIs

## Documentation

- [Okta React SDK](https://github.com/okta/okta-react)
- [Okta Auth JS](https://github.com/okta/okta-auth-js)
- [OIDC Integration Guide](../../docs/OIDC_INTEGRATION.md)
- [Security Best Practices](../../docs/SECURITY.md)

## Support

- **Issues:** [GitHub Issues](https://github.com/MikeDominic92/okta-sso-hub/issues)
- **Okta Developer Forum:** [devforum.okta.com](https://devforum.okta.com/)
- **Project Docs:** [docs/](../../docs/)

---

**Built with:** React 18 • TypeScript • Okta Auth SDK • OAuth 2.0 + PKCE
