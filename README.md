# Okta SSO Hub

[![Node.js](https://img.shields.io/badge/Node.js-18.x-green.svg)](https://nodejs.org/)
[![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)](https://www.python.org/)
[![React](https://img.shields.io/badge/React-18.x-61dafb.svg)](https://reactjs.org/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Okta](https://img.shields.io/badge/Okta-Developer-00297a.svg)](https://developer.okta.com/)

> A comprehensive IAM portfolio project demonstrating Okta integration with SAML 2.0, OIDC/OAuth 2.0, SCIM provisioning, and automated workflows.

**Certification Focus**: Okta Certified Professional/Administrator

## Table of Contents

- [Overview](#overview)
- [Architecture](#architecture)
- [Features](#features)
- [SAML vs OIDC](#saml-vs-oidc)
- [Quick Start](#quick-start)
- [Applications](#applications)
- [Automation](#automation)
- [Documentation](#documentation)
- [Security](#security)
- [Contributing](#contributing)
- [License](#license)

## Overview

This project showcases enterprise-grade Single Sign-On (SSO) implementation using Okta as the Identity Provider (IdP). It includes three fully functional applications integrated via different authentication protocols, automated user provisioning, and policy management.

### What You'll Learn

- Configure Okta SAML 2.0 applications
- Implement OIDC with Authorization Code Flow + PKCE
- Set up SCIM 2.0 for automated provisioning
- Create MFA policies and authentication flows
- Automate user lifecycle management via Okta API
- Build secure SPAs and APIs with Okta integration

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         Okta (IdP)                              │
│  - Universal Directory                                          │
│  - Authentication Policies                                      │
│  - MFA Enforcement                                              │
│  - SCIM Provisioning                                            │
└──────────────┬──────────────┬──────────────┬───────────────────┘
               │              │              │
        OIDC   │       SAML   │       API    │
               │              │              │
        ┌──────▼─────┐ ┌──────▼─────┐ ┌─────▼──────┐
        │ React SPA  │ │ Flask App  │ │  Node API  │
        │  (PKCE)    │ │   (SP)     │ │  (JWT)     │
        └────────────┘ └────────────┘ └────────────┘
               │              │              │
        ┌──────▼──────────────▼──────────────▼───────┐
        │         Backend Resources/Data             │
        └────────────────────────────────────────────┘
```

## Features

### Identity & Access Management
- ✅ **SAML 2.0 Integration** - Enterprise SSO with Flask Service Provider
- ✅ **OIDC/OAuth 2.0** - Modern authentication for React SPA
- ✅ **Passkeys/FIDO2** - Passwordless authentication with WebAuthn
- ✅ **JWT Validation** - Secure API access with token verification
- ✅ **Multi-Factor Authentication** - Configurable MFA policies
- ✅ **Session Management** - Token refresh and session handling

### Provisioning & Automation
- ✅ **SCIM 2.0 Server** - Automated user provisioning
- ✅ **Okta API Integration** - User/group management via SDK
- ✅ **Bulk Operations** - CSV import and batch processing
- ✅ **Lifecycle Workflows** - Onboarding/offboarding automation

### Security & Compliance
- ✅ **Authorization Code Flow with PKCE** - Secure OAuth flow for SPAs
- ✅ **Scope-Based Authorization** - Fine-grained API access control
- ✅ **Attribute-Based Access Control** - SAML attribute mapping
- ✅ **Audit Logging** - Track authentication events

## SAML vs OIDC

| Feature | SAML 2.0 | OIDC/OAuth 2.0 |
|---------|----------|----------------|
| **Protocol** | XML-based | JSON/REST-based |
| **Primary Use Case** | Enterprise SSO | Mobile & modern web apps |
| **Token Format** | XML assertions | JWT (JSON Web Tokens) |
| **Implementation** | Flask SAML SP | React with Okta SDK |
| **Best For** | Legacy enterprise apps | APIs and SPAs |
| **Complexity** | Higher (XML, certificates) | Lower (REST, JSON) |
| **Mobile Support** | Limited | Excellent |
| **Example App** | `flask-saml-sp/` | `react-oidc-spa/`, `node-api/` |

## Passkeys & Passwordless Authentication

**NEW in 2025**: This project now includes FIDO2/WebAuthn passkey support for phishing-resistant, passwordless authentication.

### What are Passkeys?

Passkeys are a modern authentication method that replaces passwords with cryptographic keys stored on your device. They provide:

- **Phishing-resistant authentication** - Cannot be stolen or used on fake websites
- **Passwordless login** - No passwords to remember or manage
- **Biometric convenience** - Use Touch ID, Face ID, or Windows Hello
- **Security key support** - Works with YubiKey and other FIDO2 devices
- **Industry standard** - Built on FIDO2/WebAuthn specifications

### Features

- ✅ WebAuthn credential registration and management
- ✅ Browser compatibility detection (Chrome, Firefox, Safari, Edge)
- ✅ Platform authenticator support (Touch ID, Windows Hello, Face ID)
- ✅ Security key support (YubiKey, Titan Key, etc.)
- ✅ Passkey management UI (create, view, delete)
- ✅ Comprehensive documentation with implementation guide

### Try It Out

1. Navigate to the React OIDC SPA application
2. Log in with your Okta credentials
3. Click **"Manage Passkeys"** in the dashboard
4. Register a new passkey using Touch ID, Windows Hello, or a security key
5. View and manage your registered passkeys

**See [docs/PASSKEYS.md](docs/PASSKEYS.md) for detailed implementation guide and Okta configuration.**

## Quick Start

### Prerequisites

- **Okta Developer Account** - [Sign up here](https://developer.okta.com/signup/)
- Node.js 18.x or higher
- Python 3.9 or higher
- Git

### 1. Clone the Repository

```bash
git clone https://github.com/MikeDominic92/okta-sso-hub.git
cd okta-sso-hub
```

### 2. Set Up Okta Developer Tenant

1. Create a free developer account at [developer.okta.com](https://developer.okta.com/signup/)
2. Note your Okta domain (e.g., `dev-12345678.okta.com`)
3. Create an API token: **Security → API → Tokens → Create Token**
4. Follow setup guides in `docs/` for each integration type

### 3. Configure Environment Variables

Each application has its own `.env.example` file. Copy and configure:

```bash
# React OIDC SPA
cp apps/react-oidc-spa/.env.example apps/react-oidc-spa/.env

# Flask SAML SP
cp apps/flask-saml-sp/.env.example apps/flask-saml-sp/.env

# Node.js API
cp apps/node-api/.env.example apps/node-api/.env

# Python Automation
cp automation/python/.env.example automation/python/.env
```

### 4. Run Applications

See individual application READMEs for detailed instructions:
- [React OIDC SPA](apps/react-oidc-spa/README.md)
- [Flask SAML SP](apps/flask-saml-sp/README.md)
- [Node.js API](apps/node-api/README.md)

## Applications

### 1. React OIDC SPA (`apps/react-oidc-spa/`)

Modern single-page application using Okta React SDK with Authorization Code Flow + PKCE.

**Features:**
- Secure authentication without client secrets
- Protected routes with automatic redirect
- Token management and refresh
- User profile display

**Tech Stack:** React 18, TypeScript, @okta/okta-react, React Router

**Quick Start:**
```bash
cd apps/react-oidc-spa
npm install
npm start  # Runs on http://localhost:3000
```

### 2. Flask SAML Service Provider (`apps/flask-saml-sp/`)

Enterprise SSO application demonstrating SAML 2.0 integration with Okta as IdP.

**Features:**
- SAML SSO and SLO (Single Logout)
- Attribute mapping from Okta assertions
- SP metadata generation
- Session management

**Tech Stack:** Flask, python3-saml

**Quick Start:**
```bash
cd apps/flask-saml-sp
pip install -r requirements.txt
python app.py  # Runs on http://localhost:5000
```

### 3. Node.js Protected API (`apps/node-api/`)

RESTful API with JWT token validation and scope-based authorization.

**Features:**
- Okta JWT verification middleware
- Scope and claims validation
- Protected endpoints
- CORS configuration

**Tech Stack:** Node.js, Express, @okta/jwt-verifier

**Quick Start:**
```bash
cd apps/node-api
npm install
npm start  # Runs on http://localhost:8080
```

## Automation

### Python SDK Integration (`automation/python/`)

Comprehensive Okta API automation scripts:

- **`okta_client.py`** - Reusable Okta SDK wrapper
- **`create_users.py`** - Single and bulk user creation
- **`bulk_operations.py`** - CSV import, batch updates
- **`group_management.py`** - Group CRUD operations

**Example:**
```bash
cd automation/python
pip install -r requirements.txt
python create_users.py --csv users.csv
```

### Okta Workflows (`automation/workflows/`)

Pre-built workflow templates (JSON format):

- **`new_hire_onboarding.json`** - Automated user provisioning flow
- **`offboarding.json`** - Deprovisioning and session revocation
- **`password_reset_notification.json`** - Alert on password changes

Import these into Okta Workflows console or use as reference for API-based automation.

## Deployment Verification

This project is fully functional with working SAML, OIDC, and SCIM integrations. Comprehensive deployment evidence is available in [docs/DEPLOYMENT_EVIDENCE.md](docs/DEPLOYMENT_EVIDENCE.md).

### Quick Verification Commands

```bash
# 1. Verify Okta org is accessible
curl "https://dev-YOUR_ORG.okta.com/api/v1/org" \
  -H "Authorization: SSWS ${OKTA_API_TOKEN}"

# 2. Test React OIDC SPA
cd apps/react-oidc-spa && npm start
# Open http://localhost:3000 - login redirects to Okta

# 3. Test Flask SAML SP
cd apps/flask-saml-sp && python app.py
# Open http://localhost:5000 - SAML SSO flow

# 4. Test Node.js API with JWT
curl http://localhost:8080/api/protected/profile \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

### Sample Evidence Included

- Complete SAML assertion XML (sanitized)
- Decoded OIDC/JWT tokens with all claims
- SCIM user provisioning request/response examples
- Protected API endpoint responses showing JWT validation
- Test execution results with 96% code coverage

See [Deployment Evidence](docs/DEPLOYMENT_EVIDENCE.md) for complete verification and outputs.

## Documentation

Comprehensive guides in the `docs/` directory:

### Setup Guides
- [Deployment Evidence](docs/DEPLOYMENT_EVIDENCE.md) - Proof of functionality
- [Okta Initial Setup](docs/OKTA_SETUP.md) - Developer tenant configuration
- [SAML Integration](docs/SAML_INTEGRATION.md) - Configure SAML app in Okta
- [OIDC Integration](docs/OIDC_INTEGRATION.md) - Create OIDC application
- [Passkeys/FIDO2](docs/PASSKEYS.md) - Passwordless authentication with WebAuthn
- [SCIM Provisioning](docs/SCIM_PROVISIONING.md) - Automated user sync
- [MFA Policies](docs/MFA_POLICIES.md) - Multi-factor authentication setup

### Architecture & Decisions
- [ADR-001: Okta Integration](docs/decisions/ADR-001-okta-integration.md) - Why Okta for SSO demo
- [Cost Analysis](docs/COST_ANALYSIS.md) - Free tier breakdown ($0)
- [Security Best Practices](docs/SECURITY.md) - OAuth/SAML security guidelines

## Security

This project implements industry-standard security practices:

- **Authorization Code Flow with PKCE** - Eliminates client secret requirement for SPAs
- **JWT Signature Validation** - Cryptographic verification of tokens
- **Scope-Based Authorization** - Fine-grained access control
- **Short-Lived Tokens** - 1-hour access token expiration
- **Secure Token Storage** - SessionStorage for SPAs, memory for APIs
- **HTTPS Required** - Redirect URIs enforce TLS
- **No Secrets in Code** - Environment variables for all sensitive data

See [SECURITY.md](docs/SECURITY.md) for detailed security documentation.

## Testing

Run the test suite:

```bash
# Python tests
cd tests
pytest test_okta_client.py
pytest test_jwt_verification.py

# Node.js tests (if implemented)
cd apps/node-api
npm test
```

## Cost Analysis

**Total Cost: $0/month**

This project uses Okta's free developer tier:
- 1,000 monthly active users
- Unlimited applications
- All authentication protocols (SAML, OIDC, SCIM)
- MFA support (Okta Verify, SMS, Email)
- API access with rate limits

See [COST_ANALYSIS.md](docs/COST_ANALYSIS.md) for details.

## Project Structure

```
okta-sso-hub/
├── apps/
│   ├── react-oidc-spa/      # React SPA with OIDC
│   ├── flask-saml-sp/       # Flask SAML Service Provider
│   └── node-api/            # Node.js API with JWT validation
├── automation/
│   ├── python/              # Okta SDK automation scripts
│   └── workflows/           # Okta Workflows JSON templates
├── scim/                    # SCIM 2.0 server implementation
├── policies/                # Authentication policy documentation
├── docs/                    # Comprehensive documentation
└── tests/                   # Test suites
```

## Contributing

Contributions are welcome! Please read [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/my-feature`
3. Commit changes: `git commit -m 'Add some feature'`
4. Push to branch: `git push origin feature/my-feature`
5. Submit a pull request

## Roadmap

- [ ] Add Terraform configuration for Okta resources
- [ ] Implement Angular SPA example
- [ ] Add Spring Boot SAML application
- [ ] Create Docker Compose setup
- [ ] Add Postman collection for API testing
- [ ] Implement webhook handlers for Okta events

## License

This project is licensed under the MIT License - see [LICENSE](LICENSE) file for details.

## Frontend Dashboard

A modern React/Next.js frontend is available with an Okta Flow aesthetic:

```bash
cd frontend
npm install
npm run dev
```

Frontend will open at `http://localhost:3000`

**Frontend Screenshots:**

| Dashboard | Application Catalog | Federation |
|-----------|---------------------|------------|
| ![Dashboard](docs/screenshots/okta_dashboard_1764620382675.png) | ![Apps](docs/screenshots/okta_apps_1764620414608.png) | ![Federation](docs/screenshots/okta_federation_1764620443193.png) |

See [Frontend Walkthrough](docs/FRONTEND_WALKTHROUGH.md) for full documentation.

## Acknowledgments

- [Okta Developer Documentation](https://developer.okta.com/docs/)
- [SAML 2.0 Specification](http://docs.oasis-open.org/security/saml/Post2.0/sstc-saml-tech-overview-2.0.html)
- [OAuth 2.0 and OIDC](https://oauth.net/2/)
- [SCIM 2.0 RFC](https://datatracker.ietf.org/doc/html/rfc7644)

## Contact

**Michael Dominic**
- GitHub: [@MikeDominic92](https://github.com/MikeDominic92)
- Project: [okta-sso-hub](https://github.com/MikeDominic92/okta-sso-hub)

---

**Built for IAM Portfolio | Okta Certified Professional Preparation**
