# ADR-001: Okta Integration for SSO Demo

**Status:** Accepted
**Date:** 2025-11-30
**Decision Makers:** Michael Dominic
**Context:** IAM Portfolio Project - SSO Hub Implementation

## Context

We need to select an Identity Provider (IdP) platform for demonstrating enterprise Single Sign-On (SSO) capabilities in a portfolio project. The solution must showcase SAML 2.0, OIDC/OAuth 2.0, SCIM provisioning, and automated workflows while remaining cost-effective and aligned with industry certifications.

### Requirements

**Functional Requirements:**
- Support for SAML 2.0 and OIDC/OAuth 2.0 protocols
- SCIM 2.0 for automated provisioning
- Multi-Factor Authentication (MFA) capabilities
- RESTful API for automation
- User and group management
- Session management and policy controls

**Non-Functional Requirements:**
- Zero or minimal cost for development/demo
- Industry-recognized platform (certification value)
- Comprehensive documentation
- Production-grade security features
- Ease of setup and configuration
- Portfolio-friendly (impressive to employers)

## Decision

We will use **Okta** as the Identity Provider for this SSO demonstration project.

## Rationale

### Why Okta?

#### 1. **Free Developer Tier**
- 1,000 monthly active users (more than sufficient for demo)
- Unlimited applications
- Full protocol support (SAML, OIDC, SCIM)
- MFA included (Okta Verify, SMS, Email)
- No credit card required
- Never expires

**Cost: $0/month**

#### 2. **Industry Leadership**
- Gartner Magic Quadrant Leader for Access Management
- Used by 16,000+ enterprises globally
- Recognized certification: **Okta Certified Professional**
- Strong employer demand for Okta skills
- Modern, cloud-native platform

#### 3. **Protocol Support**
| Protocol | Support Level | Use Case |
|----------|--------------|----------|
| SAML 2.0 | Full | Enterprise SSO |
| OIDC/OAuth 2.0 | Full | Modern web/mobile apps |
| SCIM 2.0 | Full | Automated provisioning |
| WS-Federation | Full | Legacy Microsoft apps |
| LDAP | Via agent | Directory integration |

#### 4. **Developer Experience**
- **Excellent SDKs:**
  - JavaScript/React (@okta/okta-react)
  - Python (okta-sdk-python)
  - Node.js (@okta/jwt-verifier, @okta/okta-sdk-nodejs)
  - Java, .NET, Go, PHP
- **Comprehensive Documentation:**
  - Step-by-step guides
  - Code samples
  - Video tutorials
  - API reference
- **Quick Setup:**
  - App creation in minutes
  - Pre-configured templates
  - Easy metadata exchange

#### 5. **Advanced Features**
- **Okta Workflows:** No-code automation builder
- **Adaptive MFA:** Context-aware authentication
- **Universal Directory:** Centralized user store
- **API Access Management:** OAuth 2.0 authorization server
- **Event Hooks:** Real-time webhooks for events
- **Inline Hooks:** Custom logic injection

#### 6. **Learning & Certification**
- **Okta Certified Professional** certification available
- Free training courses on Okta.com
- Active community and forums
- Regular webinars and events
- Aligns with portfolio career goals (IAM specialist)

### Alternatives Considered

#### Auth0 (now Okta)
- **Pros:** Developer-friendly, good docs, free tier
- **Cons:** Merged with Okta, less enterprise-focused, smaller free tier (7,000 users but limited features)
- **Verdict:** Similar but Okta has stronger enterprise positioning

#### Azure AD (Microsoft Entra ID)
- **Pros:** Enterprise standard, comprehensive features
- **Cons:**
  - Free tier very limited (10 apps)
  - Complex setup
  - Requires Azure subscription for full features
  - Less generous free tier
- **Verdict:** More complex for demo purposes

#### Keycloak (Open Source)
- **Pros:** Free, self-hosted, full control
- **Cons:**
  - Requires infrastructure (hosting costs)
  - No certification value
  - More setup/maintenance overhead
  - Less portfolio impact (not SaaS experience)
- **Verdict:** Not ideal for cloud-focused portfolio

#### AWS Cognito
- **Pros:** AWS ecosystem integration
- **Cons:**
  - Limited free tier (50,000 MAU but costs after)
  - Less IAM-focused (more developer auth)
  - No certification pathway
  - Weaker enterprise SSO features
- **Verdict:** Better for app-specific auth, not enterprise SSO

#### Ping Identity
- **Pros:** Enterprise leader, comprehensive
- **Cons:**
  - No free tier
  - Complex pricing
  - Harder to access for demos
- **Verdict:** Not accessible for portfolio

## Consequences

### Positive

1. **Zero Cost:** Free developer account with no expiration
2. **Certification Value:** Can pursue Okta Certified Professional
3. **Portfolio Impact:** Recognized brand, impressive to employers
4. **Rapid Development:** Excellent SDKs and documentation
5. **Real-World Skills:** Directly applicable to enterprise environments
6. **Scalability:** Can demonstrate production-ready architecture
7. **Comprehensive Demo:** Supports all required protocols and features

### Negative

1. **Vendor Lock-In:** Demo is Okta-specific (mitigated by standard protocols)
2. **Free Tier Limits:** 1,000 MAU cap (not an issue for demo)
3. **Learning Curve:** Okta-specific terminology and UI
4. **Rate Limits:** API rate limits on free tier (500 requests/minute - sufficient)

### Neutral

1. **Cloud-Only:** No self-hosted option (acceptable for portfolio)
2. **Okta Branding:** Uses Okta domain for auth (professional appearance)

## Implementation Plan

### Phase 1: Foundation (Week 1)
- [ ] Create Okta developer account
- [ ] Configure Universal Directory
- [ ] Set up MFA policies
- [ ] Create API token for automation

### Phase 2: OIDC Integration (Week 1-2)
- [ ] Create OIDC application in Okta
- [ ] Build React SPA with @okta/okta-react
- [ ] Implement Authorization Code Flow + PKCE
- [ ] Configure token refresh

### Phase 3: SAML Integration (Week 2)
- [ ] Create SAML application in Okta
- [ ] Build Flask Service Provider
- [ ] Configure attribute mapping
- [ ] Test SSO and SLO flows

### Phase 4: API Protection (Week 2-3)
- [ ] Create API authorization server
- [ ] Build Node.js API with JWT verification
- [ ] Implement scope-based authorization
- [ ] Test protected endpoints

### Phase 5: Automation (Week 3)
- [ ] Develop Python SDK scripts
- [ ] Create bulk user import
- [ ] Build group management tools
- [ ] Implement lifecycle workflows

### Phase 6: SCIM Provisioning (Week 3-4)
- [ ] Build SCIM 2.0 server
- [ ] Configure Okta SCIM app
- [ ] Test user/group sync
- [ ] Implement deprovisioning

### Phase 7: Documentation (Week 4)
- [ ] Write setup guides
- [ ] Create architecture diagrams
- [ ] Document security practices
- [ ] Prepare demo walkthrough

## Metrics for Success

- ✅ All three authentication protocols working (SAML, OIDC, SCIM)
- ✅ MFA enforced on authentication flows
- ✅ Automated user lifecycle management
- ✅ Comprehensive documentation
- ✅ GitHub repository with 100+ stars (aspirational)
- ✅ Okta Certified Professional certification obtained

## References

- [Okta Developer Documentation](https://developer.okta.com/docs/)
- [Okta Free Developer Account](https://developer.okta.com/signup/)
- [Okta Certification Program](https://www.okta.com/services/certification/)
- [SAML 2.0 Specification](http://docs.oasis-open.org/security/saml/Post2.0/sstc-saml-tech-overview-2.0.html)
- [OAuth 2.0 and OIDC Specs](https://oauth.net/2/)
- [SCIM 2.0 RFC 7644](https://datatracker.ietf.org/doc/html/rfc7644)

## Revision History

| Date | Version | Changes | Author |
|------|---------|---------|--------|
| 2025-11-30 | 1.0 | Initial decision | Michael Dominic |

---

**Decision Status:** ✅ Accepted and Implemented
