# Multi-Factor Authentication (MFA) Policy

## Policy Overview

All users accessing SSO Hub applications MUST use multi-factor authentication.

## Policy Details

**Policy Name:** SSO Hub MFA Policy
**Effective Date:** 2025-11-30
**Last Updated:** 2025-11-30
**Version:** 1.0

## Scope

This policy applies to:
- All employees
- Contractors
- Third-party vendors
- All applications integrated with Okta SSO

## Requirements

### Mandatory Factors

Users MUST enroll at least one additional factor beyond password:

**Primary (Recommended):**
- Okta Verify (push notifications or TOTP)
- Hardware security key (WebAuthn/FIDO2)

**Secondary (Allowed):**
- Google Authenticator (TOTP)
- Email verification code

**Not Recommended (Use only as fallback):**
- SMS verification (vulnerable to SIM swapping)
- Security questions (phishing risk)

### Enforcement Rules

1. **All Users:**
   - MFA required for every sign-on
   - Cannot be bypassed or disabled

2. **High-Risk Scenarios (Additional Requirements):**
   - New device: Require 2 factors
   - Unusual location: Require 2 factors
   - After password reset: Immediate MFA re-enrollment

3. **Administrators:**
   - MFA required every sign-on (no "remember device")
   - Must use hardware security key or Okta Verify
   - SMS not permitted

4. **Remember Device:**
   - Standard users: 7 days maximum
   - Administrators: Not permitted
   - High-risk users: Not permitted

## Implementation

### Okta Configuration

**Authenticator Enrollment Policy:**
```
Required: Password
Required: Okta Verify OR Google Authenticator
Optional: Email, SMS
```

**Authentication Policy Rules:**

**Rule 1: Administrators**
- Condition: User in "Administrators" group
- Prompt for factor: Every sign-on
- Possession constraint: Required
- Re-authentication: Always

**Rule 2: High Risk**
- Condition: Risk level = HIGH
- Prompt for factor: Always
- Additional factors: Require 2
- Remember device: Disabled

**Rule 3: Standard Users**
- Condition: Everyone
- Prompt for factor: Every sign-on
- Remember device: 7 days
- Possession constraint: Required

## User Enrollment

### First-Time Setup

1. User logs in with username + password
2. Okta prompts for MFA enrollment
3. User selects preferred factor (recommend Okta Verify)
4. Complete enrollment process
5. Verify factor works before access granted

### Re-Enrollment

Required when:
- User loses device
- Factor compromised
- New device enrollment
- Admin resets MFA factors

## Compliance

### Monitoring

Security team monitors:
- MFA enrollment rate (target: 100%)
- Factor usage distribution
- Failed MFA attempts
- Bypass attempts (should be 0)

### Reporting

Monthly reports include:
- Users without MFA enrolled
- Users using weak factors (SMS only)
- MFA authentication failures
- Factor distribution across users

## Exceptions

**Temporary Exemptions:**

May be granted for:
- Technical issues (max 24 hours)
- Device replacement (max 48 hours)
- Emergency access (requires approval)

**Process:**
1. User submits exception request
2. Manager approves
3. Security team grants temporary exception
4. User must re-enroll MFA within exemption period

**Permanent Exceptions:**
- Not permitted
- No users exempt from MFA

## Violations

Failure to comply with this policy may result in:
- Account suspension
- Access revocation
- Disciplinary action per HR policy

## Support

**MFA Issues:**
- Help Desk: helpdesk@example.com
- Phone: 555-0100
- Self-service: Account recovery portal

**Documentation:**
- [MFA Enrollment Guide](../docs/MFA_POLICIES.md)
- [Okta Verify Setup](https://help.okta.com/okta_help.htm)

## References

- NIST SP 800-63B: Digital Identity Guidelines
- Okta Security Best Practices
- Company Information Security Policy

## Approval

**Policy Owner:** Chief Information Security Officer
**Approved By:** IT Steering Committee
**Next Review:** 2026-11-30

---

**Note:** This is a template policy for the portfolio project. Adapt for production use.
