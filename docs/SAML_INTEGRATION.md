# SAML 2.0 Integration Guide

This guide explains how to configure Okta as a SAML 2.0 Identity Provider (IdP) and integrate the Flask Service Provider application.

## Table of Contents

1. [SAML Overview](#saml-overview)
2. [Create SAML App in Okta](#create-saml-app-in-okta)
3. [Configure Flask Service Provider](#configure-flask-service-provider)
4. [Test SAML Flow](#test-saml-flow)
5. [Attribute Mapping](#attribute-mapping)
6. [Single Logout](#single-logout)
7. [Troubleshooting](#troubleshooting)

## SAML Overview

### What is SAML?

**SAML (Security Assertion Markup Language)** is an XML-based standard for exchanging authentication and authorization data between:
- **Identity Provider (IdP):** Okta - authenticates users
- **Service Provider (SP):** Flask app - provides services

### SAML Flow

```
User → SP → IdP (Okta) → SP → User accesses app
  1      2       3         4          5

1. User accesses Flask app
2. SP redirects to Okta for authentication
3. User logs in to Okta (IdP)
4. Okta sends SAML assertion to SP
5. SP validates assertion and grants access
```

### Key Components

- **SAML Assertion:** XML document containing user identity
- **SP Metadata:** Configuration data about Flask app
- **IdP Metadata:** Configuration data about Okta
- **ACS URL:** Assertion Consumer Service - where Okta sends response
- **Entity ID:** Unique identifier for SP

## Create SAML App in Okta

### Step 1: Navigate to Applications

1. Log in to Okta Admin Console: `https://dev-12345678-admin.okta.com`
2. Go to **Applications → Applications**
3. Click **Create App Integration**

### Step 2: Select SAML 2.0

1. Choose **SAML 2.0**
2. Click **Next**

### Step 3: Configure General Settings

Fill out the form:

- **App name:** Flask SAML Service Provider
- **App logo:** (Optional) Upload a logo
- **App visibility:**
  - ✅ Do not display application icon to users
  - ✅ Do not display application icon in the Okta Mobile app

Click **Next**

### Step 4: Configure SAML Settings

#### General

- **Single sign-on URL:** `http://localhost:5000/saml/acs`
  - ✅ Use this for Recipient URL and Destination URL
  - ✅ Allow this app to request other SSO URLs

- **Audience URI (SP Entity ID):** `http://localhost:5000/saml/metadata`

- **Default RelayState:** (Leave empty)

- **Name ID format:** `EmailAddress`

- **Application username:** `Email`

- **Update application username on:** `Create and update`

#### Attribute Statements (Optional)

Add custom attributes to pass to SP:

| Name | Name format | Value |
|------|-------------|-------|
| firstName | Unspecified | user.firstName |
| lastName | Unspecified | user.lastName |
| email | Unspecified | user.email |
| department | Unspecified | user.department |

#### Group Attribute Statements (Optional)

| Name | Name format | Filter | Value |
|------|-------------|--------|-------|
| groups | Unspecified | Matches regex | .* |

Click **Next**

### Step 5: Feedback

Select:
- **I'm an Okta customer adding an internal app**
- **This is an internal app that we have created**

Click **Finish**

### Step 6: Download IdP Metadata

1. Go to **Sign On** tab
2. Scroll to **SAML Signing Certificates**
3. Find the active certificate (Status: **Active**)
4. Click **Actions → View IdP Metadata**
5. Save the XML file as `apps/flask-saml-sp/saml/metadata.xml`

Alternatively, note the metadata URL:
```
https://dev-12345678.okta.com/app/exk.../sso/saml/metadata
```

### Step 7: Assign Users

1. Go to **Assignments** tab
2. Click **Assign → Assign to People**
3. Select test users (john.developer@example.com, etc.)
4. Click **Assign** then **Done**

## Configure Flask Service Provider

### Step 1: Install Dependencies

```bash
cd apps/flask-saml-sp
pip install -r requirements.txt
```

### Step 2: Configure SAML Settings

Edit `apps/flask-saml-sp/saml/settings.json`:

```json
{
  "strict": true,
  "debug": true,
  "sp": {
    "entityId": "http://localhost:5000/saml/metadata",
    "assertionConsumerService": {
      "url": "http://localhost:5000/saml/acs",
      "binding": "urn:oasis:names:tc:SAML:2.0:bindings:HTTP-POST"
    },
    "singleLogoutService": {
      "url": "http://localhost:5000/saml/sls",
      "binding": "urn:oasis:names:tc:SAML:2.0:bindings:HTTP-Redirect"
    },
    "NameIDFormat": "urn:oasis:names:tc:SAML:1.1:nameid-format:emailAddress",
    "x509cert": "",
    "privateKey": ""
  },
  "idp": {
    "entityId": "http://www.okta.com/exk...",
    "singleSignOnService": {
      "url": "https://dev-12345678.okta.com/app/dev-12345678_flasksamlsp_1/exk.../sso/saml",
      "binding": "urn:oasis:names:tc:SAML:2.0:bindings:HTTP-Redirect"
    },
    "singleLogoutService": {
      "url": "https://dev-12345678.okta.com/app/dev-12345678_flasksamlsp_1/exk.../slo/saml",
      "binding": "urn:oasis:names:tc:SAML:2.0:bindings:HTTP-Redirect"
    },
    "x509cert": "MIIDpDCCAoygAwIBAgIGAY..."
  }
}
```

### Step 3: Extract IdP Configuration from Metadata

Open the downloaded `metadata.xml` and extract:

1. **entityId:** Value of `<EntityDescriptor entityID="...">`
2. **SSO URL:** Value of `<SingleSignOnService Location="...">`
3. **SLO URL:** Value of `<SingleLogoutService Location="...">`
4. **x509cert:** Value inside `<X509Certificate>` tags (remove whitespace/newlines)

Update `settings.json` with these values.

### Step 4: Run Flask Application

```bash
python app.py
```

Output:
```
 * Running on http://localhost:5000
 * Debug mode: on
```

## Test SAML Flow

### Step 1: Access Application

1. Open browser: `http://localhost:5000`
2. Click **Login with SAML**

### Step 2: Redirect to Okta

- Browser redirects to Okta login page
- URL will be: `https://dev-12345678.okta.com/app/...`

### Step 3: Authenticate

1. Enter test user credentials:
   - Username: `john.developer@example.com`
   - Password: (your password)
2. Complete MFA if prompted
3. Click **Sign In**

### Step 4: SAML Assertion

- Okta generates SAML assertion (XML)
- Browser POSTs assertion to ACS URL: `http://localhost:5000/saml/acs`
- Flask validates signature and extracts attributes

### Step 5: Access Granted

- Flask creates session
- User redirected to dashboard
- Display user attributes from SAML assertion

### Expected Dashboard Output

```
Welcome, John Developer!

User Attributes:
- Email: john.developer@example.com
- First Name: John
- Last Name: Developer
- Department: Engineering
- Groups: Everyone, Developers
```

## Attribute Mapping

### Standard Attributes

Okta sends these by default in SAML assertion:

| Okta Attribute | SAML NameID/Attribute | Description |
|----------------|----------------------|-------------|
| user.email | NameID | User's email (if format is EmailAddress) |
| user.login | Subject | User's login |
| user.firstName | firstName | First name |
| user.lastName | lastName | Last name |

### Custom Attributes

To pass custom attributes:

1. In Okta app, go to **Sign On** tab
2. Click **Edit** in **SAML 2.0** section
3. Scroll to **Attribute Statements**
4. Add attributes:

```
Name: department
Value: user.department

Name: title
Value: user.title

Name: employeeId
Value: user.employeeId
```

5. Save

### Access in Flask

```python
from flask import session

@app.route('/dashboard')
def dashboard():
    attributes = session.get('samlUserdata', {})

    email = attributes.get('email', [''])[0]
    first_name = attributes.get('firstName', [''])[0]
    last_name = attributes.get('lastName', [''])[0]
    department = attributes.get('department', [''])[0]

    return render_template('dashboard.html',
        email=email,
        first_name=first_name,
        last_name=last_name,
        department=department
    )
```

## Single Logout (SLO)

### Configure SLO in Okta

1. In SAML app, go to **Sign On** tab
2. Click **Edit**
3. Enable **Single Logout**:
   - **SLO URL:** `http://localhost:5000/saml/sls`
   - **SP Issuer:** `http://localhost:5000/saml/metadata`
4. Save

### Implement in Flask

```python
@app.route('/logout')
def logout():
    auth = init_saml_auth()
    slo_url = auth.logout()

    # Clear local session
    session.clear()

    # Redirect to Okta SLO
    return redirect(slo_url)

@app.route('/saml/sls', methods=['GET', 'POST'])
def sls():
    """Single Logout Service"""
    auth = init_saml_auth()

    # Process SLO response
    auth.process_slo()

    errors = auth.get_errors()
    if errors:
        print("SLO errors:", errors)

    # Clear session and redirect
    session.clear()
    return redirect('/')
```

### Test SLO

1. Log in via SAML
2. Click **Logout** in Flask app
3. Verify:
   - Flask session cleared
   - Redirected to Okta
   - Okta session ended
   - Redirected back to Flask
4. Try accessing protected page - should require new login

## Troubleshooting

### SAML Response Validation Errors

**Problem:** `Invalid SAML Response`
**Solution:**
- Check IdP metadata is up-to-date
- Verify x509cert in settings.json matches Okta certificate
- Ensure clocks are synchronized (SAML assertions are time-sensitive)
- Enable debug mode: `"debug": true` in settings.json

### Redirect Loop

**Problem:** Infinite redirect between SP and IdP
**Solution:**
- Verify ACS URL matches exactly: `http://localhost:5000/saml/acs`
- Check RelayState is not causing issues
- Clear browser cookies and cache
- Check Flask session configuration

### Attributes Not Received

**Problem:** SAML attributes not appearing in Flask
**Solution:**
- Verify attribute statements configured in Okta
- Check attribute names match (case-sensitive)
- Enable SAML tracer browser extension to view assertion
- Log raw SAML response in Flask for debugging

### Certificate Errors

**Problem:** `Certificate verification failed`
**Solution:**
- Download latest IdP metadata from Okta
- Extract x509cert correctly (no whitespace, newlines)
- Check certificate hasn't expired in Okta
- Verify `strict` mode settings

### ACS URL Not Allowed

**Problem:** `The SAML SSO request specified an invalid Reply URL`
**Solution:**
- Verify ACS URL in Okta app matches Flask configuration
- Check "Allow this app to request other SSO URLs" is enabled
- Ensure no trailing slashes: use `/saml/acs` not `/saml/acs/`

## SAML Debugging Tools

### Browser Extensions

- **SAML-tracer** (Firefox/Chrome): Capture SAML requests/responses
- **SAML Chrome Panel** (Chrome): View SAML messages in DevTools

### Online Tools

- **SAMLtool.com**: Decode and validate SAML assertions
- **samltool.io**: SAML debugging toolkit

### Flask Debug Mode

Enable verbose logging:

```python
import logging
logging.basicConfig(level=logging.DEBUG)

# In app.py
if __name__ == '__main__':
    app.run(debug=True, port=5000)
```

## Production Considerations

### HTTPS Required

For production deployment:

1. Update URLs to use HTTPS:
   ```json
   "assertionConsumerService": {
     "url": "https://your-domain.com/saml/acs"
   }
   ```

2. Obtain SSL certificate (Let's Encrypt, commercial CA)

3. Configure web server (Nginx, Apache) with TLS

### SP Certificates

Generate SP signing certificate:

```bash
openssl req -new -x509 -days 3652 -nodes \
  -out sp.crt -keyout sp.key
```

Add to `settings.json`:
```json
"sp": {
  "x509cert": "...",
  "privateKey": "..."
}
```

### Security Headers

Add security headers in Flask:

```python
@app.after_request
def set_security_headers(response):
    response.headers['X-Frame-Options'] = 'DENY'
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['Strict-Transport-Security'] = 'max-age=31536000'
    return response
```

## Next Steps

- [Configure OIDC Integration](OIDC_INTEGRATION.md)
- [Set up MFA Policies](MFA_POLICIES.md)
- [Implement SCIM Provisioning](SCIM_PROVISIONING.md)

## References

- [SAML 2.0 Specification](http://docs.oasis-open.org/security/saml/Post2.0/sstc-saml-tech-overview-2.0.html)
- [Okta SAML Documentation](https://developer.okta.com/docs/guides/build-sso-integration/saml2/main/)
- [python3-saml Documentation](https://github.com/SAML-Toolkits/python3-saml)

---

**SAML Integration Complete!** Your Flask app now supports enterprise SSO.
