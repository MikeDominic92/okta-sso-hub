# Multi-Factor Authentication (MFA) Policies

This guide covers configuring MFA policies in Okta for enhanced security.

## Table of Contents

1. [MFA Overview](#mfa-overview)
2. [Enable Authenticators](#enable-authenticators)
3. [Create MFA Policies](#create-mfa-policies)
4. [Adaptive MFA](#adaptive-mfa)
5. [User Enrollment](#user-enrollment)
6. [Testing MFA](#testing-mfa)
7. [Best Practices](#best-practices)

## MFA Overview

### What is MFA?

**Multi-Factor Authentication** requires users to provide two or more verification factors:

1. **Something you know** - Password
2. **Something you have** - Phone, security key
3. **Something you are** - Biometrics (fingerprint, face)

### Supported Authenticators

Okta supports multiple MFA methods:

| Authenticator | Type | User Experience | Security Level |
|---------------|------|-----------------|----------------|
| Okta Verify | Push notification | Tap "Yes" on phone | High |
| Okta Verify (TOTP) | Time-based code | Enter 6-digit code | High |
| Google Authenticator | TOTP | Enter 6-digit code | High |
| SMS Authentication | SMS code | Receive text message | Medium |
| Voice Call | Voice code | Receive phone call | Medium |
| Email | Email code | Check email | Low |
| Security Key (WebAuthn) | Hardware token | Insert USB key | Very High |
| Security Question | Knowledge | Answer question | Low |

## Enable Authenticators

### Step 1: Access Authenticators

1. Log in to Okta Admin Console
2. Go to **Security → Authenticators**
3. Review enrolled authenticators

### Step 2: Add Okta Verify

1. If not already active, click **Add Authenticator**
2. Select **Okta Verify**
3. Click **Add**
4. Configure:
   - **User authentication:** Required
   - **Device type:** Any (iOS, Android, desktop)
   - **Additional verification:**
     - ✅ Enable push notifications
     - ✅ Enable TOTP
     - ✅ Enable biometrics (optional)
5. Click **Save**

### Step 3: Add Google Authenticator

1. Click **Add Authenticator**
2. Select **Google Authenticator**
3. Click **Add**
4. Configure settings
5. Click **Save**

### Step 4: Add Email Authenticator

1. Click **Add Authenticator**
2. Select **Email**
3. Click **Add**
4. Configure:
   - **Verification code length:** 6 digits
   - **Verification code lifetime:** 5 minutes
5. Click **Save**

### Step 5: Add SMS Authenticator

1. Click **Add Authenticator**
2. Select **Phone (SMS)**
3. Click **Add**
4. Configure SMS settings
5. Click **Save**

**Note:** SMS may require Okta telephony credits or Twilio integration.

### Step 6: Authenticator Enrollment Policy

1. Go to **Security → Authenticators → Enrollment**
2. Click **Edit** on default policy
3. Configure required authenticators:
   - **Password:** Required
   - **Okta Verify:** Required
   - **Email:** Optional
   - **SMS:** Optional
4. Set **Additional authenticator requirements:**
   - Require at least **1** additional authenticator
5. Click **Save**

## Create MFA Policies

### Step 1: Create New Policy

1. Go to **Security → Authentication Policies**
2. Click **Add a Policy**
3. Configure:
   - **Name:** SSO Hub MFA Policy
   - **Description:** Enforce MFA for all SSO Hub applications with adaptive rules
4. Click **Create Policy**

### Step 2: Add Basic MFA Rule

1. Click **Add Rule**
2. Configure:
   - **Rule name:** Require MFA for All Users
   - **IF:**
     - User's group membership includes: **Everyone**
   - **AND:**
     - User is accessing: **Any application assigned to this policy**
   - **THEN:**
     - **Access:** Allowed after successful authentication
     - **Prompt for factor:** Every sign-on (most secure)
     - **Re-authentication frequency:** Every time
   - **Possession constraint:**
     - ✅ Require possession constraint
3. Click **Create Rule**

### Step 3: Add Adaptive Rule (Risk-Based)

Create rule for high-risk scenarios:

1. Click **Add Rule**
2. Configure:
   - **Rule name:** High Risk - Step-Up MFA
   - **IF:**
     - User's group membership includes: **Everyone**
   - **AND:**
     - User is accessing: **Any application**
   - **AND:**
     - User's risk level is: **High**
   - **THEN:**
     - **Access:** Challenge
     - **Prompt for factor:** Always (cannot be remembered)
     - **Re-authentication frequency:** Every time
     - **Possession constraint:** Required
     - **Additional factors:** Require 2 factors
3. Click **Create Rule**

Priority: Place this rule **above** the basic MFA rule.

### Step 4: Add Location-Based Rule

Require MFA for users outside office network:

1. Create network zone:
   - Go to **Security → Networks**
   - Click **Add Zone**
   - Configure:
     - **Name:** Office Network
     - **Zone type:** IP
     - **Gateway IPs:** Your office IP range
   - Click **Save**

2. Create authentication rule:
   - Go to **Security → Authentication Policies → SSO Hub MFA Policy**
   - Click **Add Rule**
   - Configure:
     - **Rule name:** Require MFA Outside Office
     - **IF:**
       - User's IP is: **Not in zone** → **Office Network**
     - **AND:**
       - User is accessing: **Any application**
     - **THEN:**
       - Prompt for factor: **Every sign-on**
   - Click **Create Rule**

### Step 5: Assign Applications to Policy

1. Go to **Applications → React OIDC SPA**
2. Click **Sign On** tab
3. Under **Sign On Policy**, select: **SSO Hub MFA Policy**
4. Click **Save**

Repeat for Flask SAML app and other applications.

## Adaptive MFA

### Enable ThreatInsight

1. Go to **Security → General**
2. Scroll to **ThreatInsight**
3. Click **Edit**
4. Configure:
   - ✅ **Enable ThreatInsight**
   - **Action:** Log and enforce (block requests)
   - **Network zones to exclude:** Office Network
5. Click **Save**

### Risk Signals

ThreatInsight detects:
- **IP reputation:** Known malicious IPs
- **Anomalous location:** Login from unusual country
- **Velocity:** Multiple failed attempts
- **Impossible travel:** Login from distant locations too quickly
- **Anonymous proxy:** VPN/Tor usage

### Configure Risk Scoring

1. Go to **Security → Authentication Policies → SSO Hub MFA Policy**
2. Edit high-risk rule
3. Adjust risk level threshold:
   - **Low:** Minor anomalies
   - **Medium:** Moderate suspicious activity
   - **High:** Strong indicators of compromise

## User Enrollment

### Self-Service Enrollment

Users enroll MFA factors during first login:

1. User logs in with username + password
2. Okta prompts: "Set up multi-factor authentication"
3. User selects factor (Okta Verify, Email, SMS)
4. Completes enrollment process
5. MFA active for future logins

### Okta Verify Enrollment Flow

1. **Download app:**
   - iOS: App Store
   - Android: Google Play
   - Desktop: Download from Okta

2. **Scan QR code:**
   - Open Okta Verify app
   - Tap "Add Account"
   - Scan QR code displayed in browser

3. **Verify setup:**
   - Okta sends test push notification
   - User taps "Approve"
   - Enrollment complete

### Email Enrollment Flow

1. Okta sends verification code to user's email
2. User checks email
3. Enter 6-digit code
4. Email factor enrolled

### Admin-Initiated Enrollment

Force user to enroll:

1. Go to **Directory → People**
2. Select user
3. Click **More Actions → Reset Multi-factor**
4. Confirm reset
5. User must re-enroll on next login

## Testing MFA

### Test Okta Verify Push

1. Open incognito browser
2. Go to `http://localhost:3000` (React app)
3. Click **Login**
4. Enter credentials:
   - Username: `john.developer@example.com`
   - Password: (password)
5. Click **Sign In**
6. MFA prompt appears: "Verify it's you"
7. Check phone for Okta Verify push notification
8. Tap **Yes, it's me**
9. Browser automatically logs in

### Test Email MFA

1. During MFA prompt, select **Email** factor
2. Click **Send code**
3. Check email inbox
4. Copy 6-digit code
5. Enter code in browser
6. Click **Verify**
7. Access granted

### Test TOTP (Time-Based Code)

1. During MFA prompt, select **Okta Verify** or **Google Authenticator**
2. Open authenticator app
3. Find 6-digit code for Okta account
4. Enter code in browser
5. Click **Verify**
6. Access granted

### Test Adaptive MFA

Simulate high-risk login:

1. Use VPN to change IP address
2. Clear browser cookies
3. Attempt login
4. Observe additional challenges:
   - Security question
   - Additional factor required
   - Account temporarily locked

## Best Practices

### Security Recommendations

1. **Require MFA for all users**
   - No exceptions for administrators
   - Use "Every sign-on" for maximum security

2. **Prefer phishing-resistant factors**
   - ✅ WebAuthn security keys (FIDO2)
   - ✅ Okta Verify push notifications
   - ⚠️ Avoid SMS (vulnerable to SIM swapping)

3. **Enable adaptive policies**
   - Use ThreatInsight
   - Configure risk-based step-up
   - Monitor authentication logs

4. **Implement grace periods**
   - Remember device for 7 days (low-risk users)
   - Require every sign-on for admins
   - Location-based exemptions for office network

5. **User education**
   - Train users on phishing
   - Encourage Okta Verify over SMS
   - Document enrollment process

### Policy Design

**Layered approach:**

1. **Default:** MFA required, can remember device
2. **High-risk:** Always prompt, multiple factors
3. **Admin accounts:** Always prompt, no remember
4. **External access:** Always prompt, IP restrictions

**Example policy structure:**

```
Priority 1: Block known malicious IPs
Priority 2: Admins - Always require MFA
Priority 3: High risk - Require 2 factors
Priority 4: Outside office - Require MFA every time
Priority 5: Inside office - Remember device 7 days
Priority 6: Default - Require MFA, remember 1 day
```

### Backup Factors

Always configure multiple factors:
- Primary: Okta Verify (push)
- Backup 1: Okta Verify (TOTP)
- Backup 2: Email
- Recovery: SMS (if available)

### Monitoring

Track MFA metrics:

1. Go to **Reports → Dashboard**
2. Review:
   - MFA enrollment rate
   - Factor usage distribution
   - Failed MFA attempts
   - High-risk authentications blocked

3. Set up alerts:
   - **Security → System Log**
   - Create alert for: Repeated MFA failures
   - Notify: Security team email

## Troubleshooting

### User Locked Out

**Problem:** User can't access authenticator
**Solution:**
- Admin resets MFA factors
- User re-enrolls on next login
- Verify backup factors configured

### Push Notification Not Received

**Problem:** Okta Verify push not appearing
**Solution:**
- Check phone internet connection
- Verify Okta Verify app is updated
- Re-enroll Okta Verify
- Use TOTP as backup

### Email Code Delayed

**Problem:** Verification email not arriving
**Solution:**
- Check spam folder
- Verify email address is correct
- Wait 5 minutes (some providers delay)
- Request new code

### MFA Not Prompting

**Problem:** Users not challenged for MFA
**Solution:**
- Verify policy is assigned to application
- Check rule conditions match user
- Review rule priority order
- Clear browser cache

## Production Deployment

### Rollout Strategy

1. **Phase 1: Pilot (Week 1)**
   - IT team only
   - Test all factors
   - Gather feedback

2. **Phase 2: Early Adopters (Week 2)**
   - Select departments
   - Monitor enrollment
   - Provide support

3. **Phase 3: Full Rollout (Week 3-4)**
   - All users
   - Communication campaign
   - Help desk ready

4. **Phase 4: Enforcement (Week 5)**
   - Remove fallback options
   - Require MFA for all apps
   - Audit compliance

### Communication Template

**Subject:** New Security Requirement: Multi-Factor Authentication

**Body:**
```
Hello Team,

Starting [DATE], we're implementing Multi-Factor Authentication (MFA)
to protect our accounts and data.

What is MFA?
MFA adds an extra layer of security by requiring a second verification
method beyond your password.

How to enroll:
1. Log in to any company application
2. Follow prompts to set up Okta Verify on your phone
3. Complete enrollment (takes 2 minutes)

Recommended factor: Okta Verify app (push notifications)

Need help?
- Enrollment guide: [LINK]
- Help desk: [EMAIL/PHONE]
- FAQs: [LINK]

This change helps keep our systems secure. Thank you for your cooperation!
```

## Next Steps

- [Review Security Best Practices](SECURITY.md)
- [Configure SCIM Provisioning](SCIM_PROVISIONING.md)
- [Explore Okta Workflows](../automation/workflows/)

## References

- [Okta MFA Documentation](https://help.okta.com/okta_help.htm?type=oie&id=ext-about-authenticators)
- [NIST MFA Guidelines](https://pages.nist.gov/800-63-3/sp800-63b.html)
- [Okta Verify Documentation](https://help.okta.com/okta_help.htm?type=oie&id=ext-okta-verify-ov)

---

**MFA Policies Complete!** Your applications now require multi-factor authentication.
