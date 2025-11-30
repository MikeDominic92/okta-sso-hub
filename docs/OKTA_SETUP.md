# Okta Developer Tenant Setup Guide

This guide walks you through setting up your Okta developer tenant for the SSO Hub project.

## Table of Contents

1. [Create Developer Account](#create-developer-account)
2. [Initial Configuration](#initial-configuration)
3. [Create API Token](#create-api-token)
4. [Configure Universal Directory](#configure-universal-directory)
5. [Set Up MFA Policies](#set-up-mfa-policies)
6. [Create Test Users](#create-test-users)
7. [Verification](#verification)

## Create Developer Account

### Step 1: Sign Up

1. Go to [developer.okta.com/signup](https://developer.okta.com/signup/)
2. Fill out the registration form:
   - **Email:** Your email address
   - **First Name:** Your first name
   - **Last Name:** Your last name
   - **Country:** Your country
3. Click **Get Started**
4. Check your email for verification
5. Click the verification link and set your password

### Step 2: Note Your Okta Domain

After signup, you'll be assigned an Okta domain:
- Format: `dev-12345678.okta.com` or `dev-12345678.oktapreview.com`
- **Save this domain** - you'll use it throughout the project

Example:
```
OKTA_DOMAIN=dev-87654321.okta.com
```

### Step 3: Initial Login

1. Go to your Okta admin dashboard: `https://dev-12345678-admin.okta.com`
2. Log in with your credentials
3. You'll see the Okta Admin Console dashboard

## Initial Configuration

### Configure Organization Settings

1. Navigate to **Settings → Account**
2. Update organization details:
   - **Organization Name:** Your name or company
   - **Technical Contact:** Your email
   - **Support Email:** Your email
3. Click **Save**

### Set Up Custom Domain (Optional)

For production-like setup:

1. Go to **Customization → Domain Name**
2. Follow instructions to add custom domain
3. Update DNS records (requires domain ownership)

**Note:** For portfolio demo, the default `*.okta.com` domain is sufficient.

## Create API Token

API tokens are required for automation scripts and programmatic access.

### Step 1: Generate Token

1. Navigate to **Security → API → Tokens**
2. Click **Create Token**
3. Enter token name: `SSO-Hub-Automation`
4. Click **Create Token**
5. **IMPORTANT:** Copy the token immediately (it won't be shown again)

### Step 2: Store Token Securely

Create a `.env` file in project root:

```bash
# C:\Users\jae2j\Projects\IAM-Portfolio\okta-sso-hub\.env
OKTA_DOMAIN=dev-12345678.okta.com
OKTA_API_TOKEN=00abcdefghijklmnopqrstuvwxyz1234567890ABCD
```

**Security Warning:**
- Never commit `.env` to Git
- Never share your API token
- Rotate tokens regularly (every 90 days)
- Use separate tokens for different environments

## Configure Universal Directory

Universal Directory is Okta's centralized user store.

### Step 1: Review Default Profile

1. Go to **Directory → Profile Editor**
2. Click **User (default)**
3. Review default attributes:
   - Email (required)
   - First Name (required)
   - Last Name (required)
   - Login (required)
   - Mobile Phone
   - Department
   - Organization
   - Title

### Step 2: Add Custom Attributes (Optional)

For advanced demos, add custom attributes:

1. Click **Add Attribute**
2. Configure:
   - **Display Name:** Employee ID
   - **Variable Name:** employeeId
   - **Data Type:** String
   - **Attribute Length:** 10
3. Click **Save**

Repeat for other custom attributes:
- Cost Center
- Location
- Manager Email

### Step 3: Configure Password Policy

1. Go to **Security → Authenticators**
2. Click **Password**
3. Click **Edit**
4. Configure password requirements:
   - **Minimum Length:** 8 characters
   - **Complexity:** At least 3 of the following:
     - Lowercase letter
     - Uppercase letter
     - Number
     - Symbol
   - **Password Age:** 90 days
   - **Password History:** 4 passwords
   - **Lockout:** 5 attempts, 10 minutes
5. Click **Save**

## Set Up MFA Policies

Multi-Factor Authentication is crucial for security demos.

### Step 1: Enable Authenticators

1. Go to **Security → Authenticators**
2. Ensure these are **Active:**
   - ✅ Okta Verify
   - ✅ Email
   - ✅ SMS (if phone number available)
3. Click **Add Authenticator** if needed

### Step 2: Create MFA Policy

1. Go to **Security → Authentication Policies**
2. Click **Add a Policy**
3. Configure:
   - **Name:** SSO Hub MFA Policy
   - **Description:** Enforce MFA for all SSO Hub applications
4. Click **Create Policy**

### Step 3: Add MFA Rule

1. Click **Add Rule** in the new policy
2. Configure:
   - **Rule Name:** Require MFA
   - **IF:** User's group membership includes: `Everyone`
   - **AND:** User is accessing: `Any application`
   - **THEN:** Prompt for factor: `Every sign-on`
   - **Factors:** Okta Verify, Email, SMS
3. Click **Create Rule**

### Step 4: Assign Applications to Policy

When creating OIDC/SAML apps later, assign them to this policy.

## Create Test Users

Create sample users for testing SSO flows.

### Method 1: Via Admin Console (Manual)

1. Go to **Directory → People**
2. Click **Add Person**
3. Fill out form:
   - **First Name:** John
   - **Last Name:** Developer
   - **Username:** john.developer@example.com
   - **Primary Email:** john.developer@example.com
   - **Password:** Set by admin or user
4. Click **Save**

Repeat for additional test users:
- `jane.admin@example.com` (admin user)
- `bob.user@example.com` (standard user)

### Method 2: Via Python Script (Bulk)

Use the automation script (after setup):

```bash
cd automation/python
python create_users.py --csv test_users.csv
```

Sample `test_users.csv`:
```csv
firstName,lastName,email,login,mobilePhone
John,Developer,john.developer@example.com,john.developer@example.com,+15551234567
Jane,Admin,jane.admin@example.com,jane.admin@example.com,+15551234568
Bob,User,bob.user@example.com,bob.user@example.com,+15551234569
```

### Method 3: Via API (Curl)

```bash
curl -X POST "https://dev-12345678.okta.com/api/v1/users?activate=true" \
-H "Accept: application/json" \
-H "Content-Type: application/json" \
-H "Authorization: SSWS ${OKTA_API_TOKEN}" \
-d '{
  "profile": {
    "firstName": "John",
    "lastName": "Developer",
    "email": "john.developer@example.com",
    "login": "john.developer@example.com"
  },
  "credentials": {
    "password": { "value": "SecureP@ssw0rd!" }
  }
}'
```

## Verification

### Checklist

Verify your Okta tenant is ready:

- [ ] Developer account created and verified
- [ ] Okta domain noted: `dev-________.okta.com`
- [ ] API token created and saved in `.env`
- [ ] Password policy configured (8+ chars, complexity)
- [ ] MFA policy created and activated
- [ ] At least 3 test users created
- [ ] Universal Directory reviewed
- [ ] Admin Console accessible

### Test API Access

Verify your API token works:

```bash
curl -X GET "https://dev-12345678.okta.com/api/v1/users?limit=5" \
-H "Accept: application/json" \
-H "Authorization: SSWS ${OKTA_API_TOKEN}"
```

Expected response:
```json
[
  {
    "id": "00u...",
    "status": "ACTIVE",
    "profile": {
      "firstName": "John",
      "lastName": "Developer",
      "email": "john.developer@example.com",
      ...
    }
  },
  ...
]
```

### Test User Login

1. Open incognito/private browser window
2. Go to `https://dev-12345678.okta.com`
3. Log in with test user credentials
4. Verify MFA prompt appears
5. Complete MFA enrollment (Okta Verify or Email)
6. Verify successful login to Okta dashboard

## Next Steps

Now that your Okta tenant is configured:

1. **OIDC Integration:** [Set up React OIDC SPA](OIDC_INTEGRATION.md)
2. **SAML Integration:** [Configure Flask SAML app](SAML_INTEGRATION.md)
3. **SCIM Provisioning:** [Enable automated provisioning](SCIM_PROVISIONING.md)
4. **MFA Configuration:** [Advanced MFA policies](MFA_POLICIES.md)

## Troubleshooting

### Can't Access Admin Console

**Problem:** 404 or access denied
**Solution:** Use the correct admin URL: `https://dev-12345678-admin.okta.com`

### API Token Not Working

**Problem:** 401 Unauthorized
**Solution:**
- Verify token in `.env` matches created token
- Ensure no extra spaces or quotes
- Check token hasn't been revoked
- Recreate token if needed

### MFA Not Prompting

**Problem:** Users not prompted for MFA
**Solution:**
- Verify MFA policy is active
- Check rule conditions match user
- Ensure application is assigned to policy
- Clear browser cache and retry

### Rate Limiting

**Problem:** 429 Too Many Requests
**Solution:**
- Free tier limit: 500 requests/minute
- Implement exponential backoff
- Cache responses when possible
- Contact Okta support for higher limits

## Additional Resources

- [Okta Developer Documentation](https://developer.okta.com/docs/)
- [Okta API Reference](https://developer.okta.com/docs/reference/)
- [Okta Community Forums](https://devforum.okta.com/)
- [Okta Status Page](https://status.okta.com/)
- [Okta Admin Console Guide](https://help.okta.com/okta_help.htm?type=oie&id=ext-admin-console)

## Support

- **Okta Developer Forum:** [devforum.okta.com](https://devforum.okta.com/)
- **GitHub Issues:** [Report project-specific issues](https://github.com/MikeDominic92/okta-sso-hub/issues)
- **Email:** developers@okta.com (Okta Developer Support)

---

**Setup Complete!** Your Okta tenant is ready for SSO integration.
