# Session Management Policy

## Session Timeouts

### Idle Timeout

**Standard Users:**
- Web applications: 30 minutes
- Mobile applications: 60 minutes
- API sessions: N/A (token-based)

**Administrators:**
- Admin console: 15 minutes
- All administrative actions: Re-authenticate

### Absolute Timeout

**Maximum Session Duration:**
- Standard users: 8 hours
- Administrators: 4 hours
- After timeout: User must re-authenticate

## Token Lifetimes

### ID Tokens
- Lifetime: 1 hour
- Use: User authentication
- Storage: SessionStorage (SPAs)

### Access Tokens
- Lifetime: 1 hour
- Use: API authorization
- Renewal: Via refresh token

### Refresh Tokens
- Lifetime: 90 days (SPAs)
- Rotation: On each use
- Max use: Single use, then rotated

## Session Security

### Requirements

- HTTPS only (no HTTP)
- Secure cookies (HttpOnly, Secure, SameSite)
- CSRF protection (state parameter)
- Session fixation prevention

### Revocation

Sessions revoked on:
- Explicit logout
- Password change
- Account deactivation
- Security incident
- Admin-initiated logout

---

**Last Updated:** 2025-11-30
