# Passkeys & FIDO2 Passwordless Authentication

## Overview

This guide covers the implementation of **passkeys** (FIDO2/WebAuthn) for passwordless authentication in the Okta SSO Hub. Passkeys represent the future of authentication, offering superior security and user experience compared to traditional passwords.

## Table of Contents

- [What are Passkeys?](#what-are-passkeys)
- [FIDO2 & WebAuthn Explained](#fido2--webauthn-explained)
- [Why Passkeys?](#why-passkeys)
- [Architecture](#architecture)
- [Browser Compatibility](#browser-compatibility)
- [Implementation Guide](#implementation-guide)
- [Okta Configuration](#okta-configuration)
- [Security Benefits](#security-benefits)
- [Best Practices](#best-practices)
- [Troubleshooting](#troubleshooting)

## What are Passkeys?

**Passkeys** are a passwordless authentication method that uses public-key cryptography to replace traditional passwords. They are:

- **Phishing-resistant** - Cannot be stolen or used on fake websites
- **Unique per site** - Each website gets a unique credential
- **Private and secure** - Private keys never leave your device
- **User-friendly** - Authenticate with biometrics or PIN
- **Cross-platform** - Sync across devices via iCloud Keychain, Google Password Manager, etc.

### Key Terminology

| Term | Definition |
|------|------------|
| **Passkey** | A FIDO2 credential stored on your device for passwordless authentication |
| **FIDO2** | Fast IDentity Online 2 - the authentication standard |
| **WebAuthn** | Web Authentication API - browser API for FIDO2 |
| **Authenticator** | Device or software that creates and stores passkeys |
| **Platform Authenticator** | Built-in authenticator (Touch ID, Windows Hello, Face ID) |
| **Roaming Authenticator** | External security key (YubiKey, Titan Key) |
| **Resident Credential** | Credential stored on the authenticator itself |
| **Discoverable Credential** | Credential that can be used without entering a username |
| **Attestation** | Proof that a credential was created by a specific authenticator |
| **Relying Party (RP)** | The website/application requesting authentication |

## FIDO2 & WebAuthn Explained

### Architecture Layers

```
┌─────────────────────────────────────────────────────┐
│            User (Biometric/PIN)                     │
└─────────────────┬───────────────────────────────────┘
                  │
┌─────────────────▼───────────────────────────────────┐
│         Authenticator (Device/Security Key)         │
│  - Generates key pairs                              │
│  - Stores private keys                              │
│  - Signs challenges                                 │
└─────────────────┬───────────────────────────────────┘
                  │
┌─────────────────▼───────────────────────────────────┐
│         WebAuthn API (Browser)                      │
│  - navigator.credentials.create()                   │
│  - navigator.credentials.get()                      │
└─────────────────┬───────────────────────────────────┘
                  │
┌─────────────────▼───────────────────────────────────┐
│         Relying Party (Your App)                    │
│  - Generates challenges                             │
│  - Verifies signatures                              │
│  - Stores public keys                               │
└─────────────────────────────────────────────────────┘
```

### How It Works

#### Registration Flow

1. **User initiates registration** - Clicks "Register Passkey"
2. **Server generates challenge** - Random cryptographic challenge
3. **Browser calls WebAuthn API** - `navigator.credentials.create()`
4. **Authenticator prompts user** - Biometric or PIN verification
5. **Authenticator creates key pair** - Public/private key pair
6. **Private key stored securely** - Never leaves the authenticator
7. **Public key sent to server** - Along with attestation data
8. **Server verifies and stores** - Public key associated with user account

#### Authentication Flow

1. **User initiates login** - Visits login page
2. **Server generates challenge** - Random cryptographic challenge
3. **Browser calls WebAuthn API** - `navigator.credentials.get()`
4. **Authenticator prompts user** - Biometric or PIN verification
5. **Authenticator signs challenge** - Using private key
6. **Signature sent to server** - Along with authenticator data
7. **Server verifies signature** - Using stored public key
8. **User authenticated** - Session created

## Why Passkeys?

### Security Benefits

| Threat | Passwords | Passkeys |
|--------|-----------|----------|
| **Phishing** | Vulnerable - users can be tricked | Protected - domain-bound credentials |
| **Credential Stuffing** | Vulnerable - reused passwords | Protected - unique per site |
| **Brute Force** | Vulnerable - weak passwords | Protected - cryptographic keys |
| **Man-in-the-Middle** | Vulnerable - password interception | Protected - challenge-response |
| **Database Breach** | Critical - password hashes stolen | Low impact - only public keys exposed |
| **Social Engineering** | Vulnerable - password sharing | Protected - biometric/device-bound |

### User Experience Benefits

- **No password to remember** - Eliminate password fatigue
- **Faster authentication** - Touch ID/Face ID in seconds
- **No password resets** - No forgotten password flows
- **Seamless multi-device** - Sync via platform providers
- **Works offline** - Device-based authentication

### Compliance & Standards

- **FIDO Alliance Certified** - Industry-standard protocol
- **W3C Web Standard** - WebAuthn specification
- **NIST AAL2/AAL3** - Meets authenticator assurance levels
- **PSD2 SCA Compliant** - Strong customer authentication (EU)
- **Phishing-resistant MFA** - Required by many regulations (2025+)

## Architecture

### Components in This Project

```
okta-sso-hub/
├── apps/react-oidc-spa/src/
│   ├── components/
│   │   └── Passkeys.tsx           # Passkey management UI
│   ├── utils/
│   │   └── webauthn.ts            # WebAuthn API wrapper
│   ├── App.tsx                    # Route configuration
│   └── Dashboard.tsx              # Navigation to passkeys
└── docs/
    └── PASSKEYS.md                # This documentation
```

### Technology Stack

- **Frontend**: React 18 + TypeScript
- **WebAuthn API**: Native browser API (navigator.credentials)
- **Storage**: localStorage (demo) / Okta API (production)
- **Crypto**: Web Crypto API for challenge generation
- **Encoding**: Base64URL for binary data

## Browser Compatibility

### Supported Browsers

| Browser | Version | Platform Authenticator | Security Keys |
|---------|---------|------------------------|---------------|
| **Chrome** | 67+ | ✓ (Windows Hello, Touch ID) | ✓ |
| **Edge** | 18+ | ✓ (Windows Hello) | ✓ |
| **Firefox** | 60+ | ✓ (Windows Hello) | ✓ |
| **Safari** | 13+ | ✓ (Touch ID, Face ID) | ✓ |
| **Opera** | 54+ | ✓ (Platform-dependent) | ✓ |

### Operating System Support

| OS | Platform Authenticator | Details |
|----|------------------------|---------|
| **Windows 10/11** | Windows Hello | Biometric (face/fingerprint) or PIN |
| **macOS** | Touch ID | MacBooks with Touch Bar or M1+ chips |
| **iOS 14+** | Face ID / Touch ID | iPhone and iPad |
| **Android 9+** | Biometric / Screen Lock | Fingerprint, face, or pattern |
| **Linux** | Limited | Varies by distribution and hardware |

### Feature Detection

The implementation includes automatic feature detection:

```typescript
// Check WebAuthn support
const supported = isWebAuthnSupported();

// Check platform authenticator availability
const platformAvailable = await isPlatformAuthenticatorAvailable();
```

## Implementation Guide

### 1. Install Dependencies

The project uses standard Web APIs - no additional dependencies required:

- `navigator.credentials` - WebAuthn API
- `crypto.getRandomValues()` - Challenge generation
- `localStorage` - Passkey metadata storage (demo)

### 2. WebAuthn Utility Functions

See `apps/react-oidc-spa/src/utils/webauthn.ts`:

**Key functions:**
- `createCredential(options)` - Register new passkey
- `getCredential(options)` - Authenticate with passkey
- `isWebAuthnSupported()` - Check browser support
- `isPlatformAuthenticatorAvailable()` - Check platform authenticator
- `generateChallenge()` - Create random challenge
- `base64url.encode/decode()` - Binary data encoding

### 3. Passkeys Component

See `apps/react-oidc-spa/src/components/Passkeys.tsx`:

**Features:**
- Browser compatibility detection
- Passkey registration form
- List registered passkeys
- Delete passkeys
- Status indicators and error handling

### 4. Add Route

In `App.tsx`:

```typescript
import Passkeys from './components/Passkeys';

// Add route
<Route path="/passkeys" element={<SecureRoute><Passkeys /></SecureRoute>} />
```

### 5. Add Navigation

In `Dashboard.tsx`:

```typescript
import { useNavigate } from 'react-router-dom';

const navigate = useNavigate();

// Add button
<button onClick={() => navigate('/passkeys')}>
  Manage Passkeys
</button>
```

### 6. Testing

1. **Navigate to passkeys page**: `/passkeys`
2. **Check browser compatibility** - Should show supported status
3. **Register a passkey**:
   - Enter a name (e.g., "My MacBook Touch ID")
   - Select authenticator type (platform or security key)
   - Click "Register Passkey"
   - Complete biometric/PIN prompt
4. **View registered passkeys** - Should appear in list
5. **Delete passkey** - Click delete and confirm

## Okta Configuration

### Demo vs Production

**Current Demo Implementation:**
- Passkeys stored in browser localStorage
- Challenge generated client-side
- No server-side verification
- For demonstration and learning purposes

**Production Okta Integration:**

To integrate with Okta for production SSO:

### 1. Enable WebAuthn in Okta

1. **Log in to Okta Admin Console**
2. **Navigate to**: Security → Authenticators
3. **Click**: Add Authenticator
4. **Select**: Security Key or Biometric (WebAuthn)
5. **Configure**:
   - Enable for your org
   - Set user enrollment policy
   - Configure authenticator settings

### 2. Configure Authentication Policy

1. **Navigate to**: Security → Authentication Policies
2. **Edit your policy**:
   - Add WebAuthn as allowed authenticator
   - Set MFA requirement
   - Configure authenticator constraints

### 3. Update App Integration

1. **Navigate to**: Applications → Your App
2. **Sign On tab**:
   - Enable "Prompt for factor"
   - Select WebAuthn as allowed factor
3. **General tab**:
   - Ensure HTTPS redirect URIs
   - Enable PKCE (required for passkeys)

### 4. Implement Server-Side Verification

For production, replace client-side logic with Okta API calls:

```typescript
// Registration - Call Okta Factors API
POST /api/v1/users/{userId}/factors
{
  "factorType": "webauthn",
  "provider": "FIDO",
  "profile": {
    "authenticatorName": "My Passkey"
  }
}

// Get registration challenge from Okta
GET /api/v1/users/{userId}/factors/{factorId}/verify

// Complete registration with credential
POST /api/v1/users/{userId}/factors/{factorId}/verify
{
  "attestation": "<attestation-object>",
  "clientData": "<client-data-json>"
}

// Authentication - Verify with Okta
POST /api/v1/authn/factors/{factorId}/verify
{
  "authenticatorData": "<authenticator-data>",
  "clientData": "<client-data-json>",
  "signatureData": "<signature>"
}
```

### 5. SDK Integration

Use Okta Auth JS SDK:

```typescript
import { OktaAuth } from '@okta/okta-auth-js';

const oktaAuth = new OktaAuth({
  issuer: 'https://your-domain.okta.com/oauth2/default',
  clientId: 'your-client-id',
  // ... other config
});

// Enroll WebAuthn factor
await oktaAuth.idx.register({
  authenticators: ['webauthn']
});

// Authenticate with WebAuthn
await oktaAuth.idx.authenticate({
  authenticator: 'webauthn'
});
```

## Security Benefits

### Phishing Resistance

**How it works:**
1. **Domain binding** - Credential only works on registered domain
2. **Origin validation** - Browser enforces same-origin policy
3. **No secret to steal** - User never types or sees credential
4. **Automatic verification** - No user decision required

**Example Attack Prevented:**
```
Attacker creates: evil-okta-login.com
User visits malicious site
Even if user tries to authenticate, passkey won't work
Credential is bound to legitimate: login.okta.com
```

### Cryptographic Strength

- **Key length**: 2048-bit RSA or 256-bit ECC
- **Algorithm**: ES256 (ECDSA) or RS256 (RSA-SHA256)
- **Challenge**: 32-byte random value (256 bits of entropy)
- **Signature**: Unforgeable without private key

### Privacy Protection

- **No biometric data sent** - Biometrics stay on device
- **Anonymous credentials** - No tracking across sites
- **User consent required** - Explicit gesture for each use
- **Attestation optional** - Can register without identifying device

### Compliance Advantages

| Requirement | How Passkeys Help |
|-------------|-------------------|
| **NIST 800-63B AAL2** | Cryptographic authenticator with verifier impersonation resistance |
| **PCI DSS MFA** | Phishing-resistant second factor |
| **GDPR Privacy** | No password storage, minimal PII collection |
| **SOC 2 Access Control** | Strong authentication, audit trail |
| **PSD2 SCA** | Possession (device) + inherence (biometric) factors |

## Best Practices

### Registration

1. **Require user verification** - Set `userVerification: 'required'`
2. **Use resident keys** - Enable `residentKey: 'required'` for discoverable credentials
3. **Exclude existing credentials** - Prevent duplicate registrations
4. **Set appropriate timeout** - 60 seconds is reasonable
5. **Descriptive names** - Help users identify their passkeys
6. **Backup authenticators** - Encourage multiple passkeys

### Authentication

1. **Don't require username** - Use discoverable credentials when possible
2. **Fallback options** - Offer password or other MFA as backup
3. **Clear error messages** - Guide users when passkey fails
4. **Session handling** - Appropriate session timeouts
5. **Re-authentication** - For sensitive operations

### User Experience

1. **Progressive enhancement** - Detect and offer passkeys when available
2. **Onboarding** - Educate users about passkeys
3. **Visual indicators** - Show passkey status clearly
4. **Multi-device support** - Explain syncing across devices
5. **Migration path** - Allow gradual transition from passwords

### Security

1. **HTTPS required** - WebAuthn only works over HTTPS
2. **Origin validation** - Verify relying party ID matches domain
3. **Challenge uniqueness** - Generate fresh challenge per operation
4. **Attestation verification** - Validate authenticator attestation (optional)
5. **Rate limiting** - Prevent brute force attempts
6. **Audit logging** - Log all registration/authentication events

## Troubleshooting

### Common Issues

#### "WebAuthn not supported"

**Cause**: Browser doesn't support WebAuthn API

**Solution**:
- Update browser to latest version
- Use Chrome 67+, Firefox 60+, Safari 13+, or Edge 18+
- Check `window.PublicKeyCredential` exists

#### "Platform authenticator not available"

**Cause**: Device doesn't have built-in biometric authenticator

**Solution**:
- Use security key (cross-platform authenticator) instead
- Verify Windows Hello / Touch ID is configured
- Check device hardware compatibility

#### "Operation not allowed"

**Cause**: User cancelled prompt or gesture requirement not met

**Solution**:
- Ensure HTTPS (WebAuthn requires secure origin)
- User must explicitly trigger registration (button click)
- Check user cancelled biometric prompt

#### "Invalid state error"

**Cause**: Credential already registered

**Solution**:
- Use `excludeCredentials` to prevent re-registration
- Delete existing passkey before re-registering
- Check for duplicate credentials

#### "Security error"

**Cause**: Origin/RP ID mismatch or not HTTPS

**Solution**:
- Ensure page is served over HTTPS
- Verify `rpId` matches domain (e.g., `example.com`)
- `rpId` must be same or parent domain of origin

#### "Timeout"

**Cause**: User didn't respond within timeout period

**Solution**:
- Increase timeout (default 60 seconds)
- User may need to locate security key
- Check for system biometric prompts hidden behind windows

### Browser-Specific Issues

#### Safari

- **Issue**: Touch ID prompt may not appear
- **Solution**: Ensure user gesture (click event), not automatic trigger

#### Firefox

- **Issue**: Security key not detected
- **Solution**: Check USB permissions, try different USB port

#### Chrome on Android

- **Issue**: Screen lock not configured
- **Solution**: Set up screen lock (PIN, pattern, or biometric) in Android settings

### Testing Tips

1. **Use localhost** - Treated as secure origin (no HTTPS needed)
2. **Check console** - WebAuthn errors logged to browser console
3. **Test on real devices** - Emulators may not support authenticators
4. **Multiple browsers** - Test cross-browser compatibility
5. **Security keys** - Test both platform and roaming authenticators

### Developer Tools

#### Chrome DevTools

- **Application → WebAuthn** - Virtual authenticator for testing
- Can create virtual devices without hardware

#### Firefox DevTools

- **Web Console** - Detailed WebAuthn error messages
- `about:webauthn` - WebAuthn management page

#### Debugging

```javascript
// Enable verbose logging
localStorage.setItem('webauthn:debug', 'true');

// Check credential support
if (window.PublicKeyCredential) {
  console.log('WebAuthn supported');

  PublicKeyCredential.isUserVerifyingPlatformAuthenticatorAvailable()
    .then(available => {
      console.log('Platform authenticator:', available);
    });
}
```

## Resources

### Official Documentation

- [W3C WebAuthn Specification](https://www.w3.org/TR/webauthn-2/)
- [FIDO Alliance](https://fidoalliance.org/)
- [Okta WebAuthn Guide](https://developer.okta.com/docs/guides/webauthn/main/)
- [MDN Web Authentication API](https://developer.mozilla.org/en-US/docs/Web/API/Web_Authentication_API)

### Standards & Specifications

- [CTAP 2.1 (Client to Authenticator Protocol)](https://fidoalliance.org/specs/fido-v2.1-ps-20210615/fido-client-to-authenticator-protocol-v2.1-ps-20210615.html)
- [FIDO2 Overview](https://fidoalliance.org/fido2/)
- [WebAuthn Level 2 (W3C Recommendation)](https://www.w3.org/TR/webauthn-2/)

### Libraries & Tools

- [@simplewebauthn/browser](https://github.com/MasterKale/SimpleWebAuthn) - WebAuthn library
- [webauthn.io](https://webauthn.io/) - WebAuthn demo site
- [webauthn.me](https://webauthn.me/) - Testing tool

### Articles & Guides

- [Passkeys.dev](https://passkeys.dev/) - Comprehensive guide
- [FIDO Alliance: How FIDO Works](https://fidoalliance.org/how-fido-works/)
- [Google: Passkeys Introduction](https://developers.google.com/identity/passkeys)
- [Apple: Supporting Passkeys](https://developer.apple.com/documentation/authenticationservices/public-private_key_authentication/supporting_passkeys)

### Industry Adoption

- **Apple**: Passkeys in iOS 16+ / macOS Ventura+
- **Google**: Passkeys in Android 9+ / Chrome 108+
- **Microsoft**: Passkeys in Windows 11 22H2+
- **1Password, Dashlane, Bitwarden**: Passkey support in password managers

---

## Next Steps

1. **Test the implementation** - Try registering passkeys
2. **Review the code** - Understand WebAuthn flow
3. **Configure Okta** - Set up WebAuthn factor (production)
4. **Migrate users** - Plan passwordless transition
5. **Monitor adoption** - Track passkey usage metrics

For questions or issues, refer to the [main README](../README.md) or open a GitHub issue.

---

**Built with Okta SSO Hub | Demonstrating 2025 IAM Best Practices**
