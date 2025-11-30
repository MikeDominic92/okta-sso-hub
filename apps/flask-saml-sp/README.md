# Flask SAML Service Provider

Enterprise SSO application demonstrating SAML 2.0 integration with Okta as Identity Provider.

## Features

- **SAML 2.0 SSO** - Single Sign-On with Okta
- **Single Logout (SLO)** - Global logout across all SAML sessions
- **Attribute Mapping** - Extract user data from SAML assertions
- **SP Metadata Generation** - Auto-generate Service Provider metadata
- **Signature Validation** - Cryptographic verification of SAML assertions

## Prerequisites

- Python 3.9 or higher
- pip
- Okta Developer Account
- SAML application configured in Okta

## Setup

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure Environment Variables

Copy `.env.example` to `.env`:

```bash
cp .env.example .env
```

Edit `.env` with your configuration:

```bash
SECRET_KEY=your_secret_key_here
APP_URL=http://localhost:5000
```

### 3. Create SAML App in Okta

Follow the [SAML Integration Guide](../../docs/SAML_INTEGRATION.md) to create a SAML application in Okta.

### 4. Configure SAML Settings

Edit `saml/settings.json` with values from Okta:

- **entityId**: From Okta SAML app metadata
- **singleSignOnService.url**: SSO URL from Okta
- **singleLogoutService.url**: SLO URL from Okta
- **x509cert**: Certificate from Okta metadata (remove whitespace and newlines)

Alternatively, download IdP metadata from Okta and extract these values.

## Running the Application

```bash
python app.py
```

Application runs on: `http://localhost:5000`

## Usage

### Login Flow

1. Navigate to `http://localhost:5000`
2. Click **Login with Okta SAML**
3. Browser redirects to Okta
4. Enter credentials and complete MFA
5. Okta sends SAML assertion to ACS endpoint
6. Flask validates assertion and creates session
7. User redirected to dashboard

### Logout Flow

1. Click **Logout**
2. Flask sends SLO request to Okta
3. Okta terminates session
4. Okta sends SLO response back
5. Flask processes response and clears session

## Endpoints

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/` | GET | Landing page / Dashboard |
| `/login` | GET | Initiate SAML SSO |
| `/saml/acs` | POST | Assertion Consumer Service |
| `/saml/metadata` | GET | SP metadata XML |
| `/saml/sls` | GET/POST | Single Logout Service |
| `/logout` | GET | Initiate SP logout |
| `/attributes` | GET | View raw SAML attributes |

## Project Structure

```
flask-saml-sp/
├── app.py                      # Main Flask application
├── requirements.txt            # Python dependencies
├── .env.example                # Environment variables template
├── saml/
│   ├── settings.json           # SAML SP and IdP configuration
│   └── advanced_settings.json  # Advanced SAML security settings
└── README.md                   # This file
```

## SAML Configuration

### Service Provider (SP)

```json
{
  "entityId": "http://localhost:5000/saml/metadata",
  "assertionConsumerService": {
    "url": "http://localhost:5000/saml/acs"
  },
  "singleLogoutService": {
    "url": "http://localhost:5000/saml/sls"
  }
}
```

### Identity Provider (IdP)

Configure in `saml/settings.json`:

```json
{
  "idp": {
    "entityId": "http://www.okta.com/exk...",
    "singleSignOnService": {
      "url": "https://dev-12345678.okta.com/app/.../sso/saml"
    },
    "singleLogoutService": {
      "url": "https://dev-12345678.okta.com/app/.../slo/saml"
    },
    "x509cert": "MIIDpDCCAoyg..."
  }
}
```

## Attribute Mapping

Configure attribute statements in Okta to pass user data:

| Okta Attribute | SAML Attribute | Value |
|----------------|----------------|-------|
| firstName | firstName | user.firstName |
| lastName | lastName | user.lastName |
| email | email | user.email |
| department | department | user.department |

Access in Flask:

```python
attributes = session.get('samlUserdata', {})
first_name = attributes.get('firstName', [''])[0]
email = attributes.get('email', [''])[0]
```

## Security

### SAML Assertion Validation

python3-saml validates:
- Signature (cryptographic verification)
- Issuer (matches expected IdP)
- Audience (matches SP entity ID)
- Time validity (NotBefore/NotOnOrAfter)
- Destination (matches ACS URL)

### HTTPS in Production

Always use HTTPS for production:

```json
{
  "sp": {
    "entityId": "https://yourdomain.com/saml/metadata",
    "assertionConsumerService": {
      "url": "https://yourdomain.com/saml/acs"
    }
  }
}
```

### Secret Key

Generate strong secret key:

```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

Add to `.env`:

```bash
SECRET_KEY=a1b2c3d4e5f6...
```

## Troubleshooting

### SAML Response Validation Errors

**Error:** `Invalid SAML Response`

**Solution:**
- Verify IdP metadata is up-to-date
- Check x509cert matches Okta's current certificate
- Ensure clocks are synchronized
- Enable debug mode: `"debug": true` in settings.json

### Redirect Loop

**Problem:** Infinite redirect between Flask and Okta

**Solution:**
- Verify ACS URL matches exactly
- Check RelayState handling
- Clear browser cookies

### Attributes Not Received

**Problem:** SAML attributes missing in session

**Solution:**
- Verify attribute statements in Okta
- Check attribute names are case-sensitive
- Enable SAML tracer to view assertion

## Production Deployment

### Environment Variables

```bash
FLASK_ENV=production
SECRET_KEY=production_secret_key
APP_URL=https://yourdomain.com
```

### WSGI Server

Use Gunicorn for production:

```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

### Update Okta Configuration

1. Add production URLs to Okta SAML app
2. Update SP metadata with HTTPS URLs
3. Test SSO and SLO flows

## Documentation

- [SAML Integration Guide](../../docs/SAML_INTEGRATION.md)
- [Security Best Practices](../../docs/SECURITY.md)
- [python3-saml Documentation](https://github.com/SAML-Toolkits/python3-saml)

---

**Built with:** Flask • python3-saml • SAML 2.0
