# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [1.2.0] - 2025-12-05

### Added - Identity Lifecycle Automation & Access Governance

#### JML Workflows (Joiner/Mover/Leaver) (`automation/workflows/`)
- **new_hire_onboarding_v2.json** - Enhanced 17-step Joiner workflow
  - HRIS webhook trigger integration
  - Department-based RBAC provisioning
  - MFA enrollment automation
  - SIEM event forwarding
- **department_transfer.json** - Complete Mover workflow
  - Old access revocation with grace period
  - New department provisioning
  - Manager notification chain
- **offboarding_v2.json** - Enhanced Leaver workflow
  - Compliance hold support for legal/HR
  - Staged access revocation
  - License reclamation

#### HRIS Mock Server (`hris-mock/`)
- **FastAPI REST Server** - Complete HRIS simulation
  - Employee CRUD operations
  - SCIM 2.0 endpoints
  - Webhook delivery to Okta
- **Event Generator** - Realistic HR event simulation
  - 40% new hires, 40% movers, 20% leavers
  - Configurable event rates
- **Patterns Supported**
  - Workday integration format
  - BambooHR webhook structure
  - Rippling SCIM 2.0

#### Access Certification Module (`access-certification/`)
- **campaign.py** - Campaign management engine
  - Quarterly review campaigns
  - Segregation of Duties (SoD) reviews
  - Role attestation campaigns
- **reports.py** - Compliance reporting
  - SOC 2 CC6.x evidence
  - ISO 27001 A.9.x evidence
  - Audit-ready packages

### Why This Matters

This release addresses critical enterprise requirements:

| Problem | Solution | Impact |
|---------|----------|--------|
| Manual onboarding takes days | JML workflows automate provisioning | Day 1 productivity, zero security gaps |
| Can't test without production HRIS | Mock server simulates Workday/BambooHR | Realistic testing without risk |
| Compliance audits require proof | Access certification with evidence | SOC 2/ISO 27001 audit-ready |
| SoD conflicts go undetected | Automated conflict detection | Fraud prevention, compliance |

### Interview Questions This Answers

| Question | How This Feature Answers It |
|----------|----------------------------|
| "How do you automate identity lifecycle?" | JML workflows with 17+ step automation, HRIS webhook triggers |
| "What HRIS systems have you integrated?" | Mock server simulates Workday, BambooHR, Rippling patterns |
| "How do you handle access certification?" | Campaign management with quarterly reviews, auto-escalation |
| "How do you ensure Day 1 provisioning?" | New hire workflow provisions apps, groups, MFA in minutes |

### Compliance Alignment
- **SOC 2 CC6.1**: Logical access security through RBAC
- **SOC 2 CC6.2**: User access authentication via MFA
- **SOC 2 CC6.3**: Access authorization through group membership
- **ISO 27001 A.9.2.1**: User registration and provisioning
- **ISO 27001 A.9.2.5**: Access rights review automation

---

## [1.1.0] - 2025-12-04

### Added - Okta Workflows Integration
- **Okta Workflows API Connector** (`src/integrations/okta_workflows_connector.py`)
  - Direct API integration with Okta Workflows
  - Flow invocation and execution management
  - Workflow execution history retrieval
  - Comprehensive mock mode for demonstrations
  - HTTP session management with automatic retry logic
  - Support for flow listing, status monitoring, and metadata queries

- **Flow Executor** (`src/integrations/flow_executor.py`)
  - High-level workflow orchestration engine
  - Asynchronous flow execution with timeout handling
  - Progress monitoring with configurable polling intervals
  - Parallel and sequential multi-flow execution
  - Execution history tracking and analytics
  - Success rate calculation and reporting
  - Event callback hooks (on_start, on_complete, on_error)
  - ExecutionResult dataclass for structured result handling

- **SSO Event Trigger System** (`src/integrations/event_trigger.py`)
  - Event-driven workflow triggering based on SSO events
  - Pre-configured trigger rules for common scenarios:
    - New hire onboarding (user creation/activation)
    - Employee offboarding (user deactivation)
    - MFA remediation (login failures)
    - Password expiry notifications
    - Application access request processing
  - Configurable trigger rules with conditions and filters
  - Event-to-workflow input transformation
  - Event-workflow correlation tracking
  - Batch event processing (parallel and sequential)
  - Comprehensive event history with filtering
  - Event simulation for testing and demos
  - Support for 20+ SSO event types (authentication, MFA, lifecycle, access, password, policy)

- **Integration Module** (`src/integrations/__init__.py`)
  - Clean module interface with version management
  - Exported classes: OktaWorkflowsConnector, FlowExecutor, EventTrigger
  - Module-level documentation

### Enhanced
- **Documentation Updates**
  - Added comprehensive v1.1 section to README.md
  - Workflow integration architecture diagram
  - Quick start guide with code examples
  - Available workflow templates documentation
  - Event-driven onboarding example
  - Updated roadmap with v1.1 completion marker

- **Dependencies**
  - Added urllib3==2.1.0 for enhanced HTTP retry logic
  - Updated requirements.txt with v1.1 enhancement comments

### Features
- **Automated Remediation Workflows**
  - Trigger workflows on authentication failures
  - Auto-enroll users in MFA on enrollment issues
  - Automated access request processing

- **Identity Lifecycle Automation**
  - Automated new hire onboarding flows
  - Employee offboarding with access revocation
  - Application provisioning workflows

- **Workflow Monitoring & Analytics**
  - Real-time execution status tracking
  - Execution history with filtering capabilities
  - Success rate analytics per flow
  - Duration and performance metrics

- **Demo Mode**
  - Full-featured mock mode for all components
  - Simulated workflow executions
  - Mock event processing
  - Perfect for presentations and testing

### Technical Highlights
- Full async/await implementation using asyncio
- Type hints throughout all modules
- Comprehensive error handling and logging
- Dataclass-based data structures
- Enum-based status and event type management
- Configurable timeouts and retry logic
- Event correlation and tracking
- Callback hook system for extensibility

### Code Quality
- December 2025 v1.1 enhancement comments throughout
- Complete docstrings for all classes and methods
- Working examples in each module's `__main__` block
- PEP 8 compliant code formatting
- Structured logging with appropriate levels

## [1.0.0] - 2025-11-30

### Added
- Initial release of Okta SSO Hub
- React OIDC SPA with Authorization Code Flow + PKCE
  - Okta React SDK integration
  - Protected routes using SecureRoute
  - Token refresh handling
  - User profile dashboard
- Flask SAML Service Provider
  - python3-saml integration
  - SAML SSO and SLO endpoints
  - Attribute mapping from Okta
  - SP metadata generation
- Node.js Protected API
  - JWT verification middleware
  - Scope-based authorization
  - Protected endpoints
  - CORS configuration
- Python automation scripts
  - Okta SDK client wrapper
  - Single and bulk user creation
  - CSV import functionality
  - Group management operations
- SCIM 2.0 server implementation
  - User provisioning endpoints
  - Group synchronization
  - Deprovisioning support
- Okta Workflows templates
  - New hire onboarding flow
  - Offboarding automation
  - Password reset notifications
- Comprehensive documentation
  - Okta setup guide
  - SAML integration guide
  - OIDC integration guide
  - SCIM provisioning guide
  - MFA policy configuration
  - Security best practices
  - Cost analysis
  - ADR-001: Okta integration decision
- Authentication policy documentation
  - MFA policy templates
  - Password policy guidelines
  - Session management policies
- Test suites
  - Okta client unit tests
  - JWT verification tests
- CI/CD pipeline
  - GitHub Actions workflow
  - Automated testing
  - Code quality checks

### Security
- Implemented PKCE for OAuth flows
- JWT signature validation
- Scope-based API authorization
- Secure token storage practices
- Environment variable management
- HTTPS enforcement for redirect URIs

## [0.1.0] - 2025-11-20

### Added
- Project initialization
- Basic directory structure
- Documentation framework

---

## Release Notes

### v1.0.0 - Initial Release

This is the first production-ready release of Okta SSO Hub, a comprehensive IAM portfolio project demonstrating enterprise-grade SSO implementation.

**Highlights:**
- Three fully functional applications (React SPA, Flask SAML, Node API)
- Complete Okta integration with SAML 2.0 and OIDC/OAuth 2.0
- Automated provisioning with SCIM 2.0
- Python-based automation suite
- Production-ready security practices
- Comprehensive documentation for Okta certification preparation

**What's Included:**
- 📱 Modern React SPA with OIDC authentication
- 🔐 Enterprise SAML integration with Flask
- 🔑 JWT-protected RESTful API
- 🤖 Automated user lifecycle management
- 📚 Complete setup and integration guides
- 🧪 Test coverage for core functionality

**Getting Started:**
1. Sign up for free Okta developer account
2. Clone repository and configure environment variables
3. Follow Quick Start guide in README.md
4. Explore documentation in `docs/` directory

**Cost:** $0 (uses Okta free developer tier)

**Next Steps:**
- Review open issues for known limitations
- Check roadmap for upcoming features
- Contribute improvements via pull requests

---

[Unreleased]: https://github.com/MikeDominic92/okta-sso-hub/compare/v1.1.0...HEAD
[1.1.0]: https://github.com/MikeDominic92/okta-sso-hub/releases/tag/v1.1.0
[1.0.0]: https://github.com/MikeDominic92/okta-sso-hub/releases/tag/v1.0.0
[0.1.0]: https://github.com/MikeDominic92/okta-sso-hub/releases/tag/v0.1.0
