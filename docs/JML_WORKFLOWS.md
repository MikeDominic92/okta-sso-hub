# Joiner/Mover/Leaver (JML) Identity Lifecycle Workflows

> **Chainguard Relevance:** This documentation demonstrates enterprise-grade identity lifecycle automation using Okta Workflows and HRIS integrations - a core requirement for IT Engineer (Identity/IAM) roles.

## Overview

The JML (Joiner/Mover/Leaver) framework automates the complete identity lifecycle, ensuring:
- **Timely access provisioning** for new hires
- **Seamless access transitions** during role changes
- **Complete access revocation** upon termination
- **Full compliance** with SOC 2, ISO 27001, NIST, and GDPR

## Architecture

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         HRIS System (Source of Truth)                    │
│                    (Workday, BambooHR, Rippling, etc.)                  │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                        HRIS Sync Integration                             │
│  • SCIM 2.0 Provisioning    • Real-time Webhooks    • Scheduled Sync   │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
            ┌───────────────────────┼───────────────────────┐
            ▼                       ▼                       ▼
    ┌───────────────┐       ┌───────────────┐       ┌───────────────┐
    │    JOINER     │       │     MOVER     │       │    LEAVER     │
    │   Workflow    │       │   Workflow    │       │   Workflow    │
    └───────────────┘       └───────────────┘       └───────────────┘
            │                       │                       │
            ▼                       ▼                       ▼
    ┌─────────────────────────────────────────────────────────────────┐
    │                      Okta Universal Directory                    │
    │         • Users    • Groups    • Applications    • Policies     │
    └─────────────────────────────────────────────────────────────────┘
            │                       │                       │
            ▼                       ▼                       ▼
    ┌─────────────────────────────────────────────────────────────────┐
    │                    Downstream Systems                            │
    │  Active Directory │ Google Workspace │ Slack │ AWS │ GitHub    │
    └─────────────────────────────────────────────────────────────────┘
```

## Workflow Files

| Workflow | File | Purpose |
|----------|------|---------|
| Joiner | `new_hire_onboarding_v2.json` | New employee provisioning |
| Mover | `department_transfer.json` | Department/role transfers |
| Leaver | `offboarding_v2.json` | Employee termination |

---

## Joiner Workflow (New Hire Onboarding)

### Trigger Events
- HRIS new employee record created
- Manual user creation via Okta Admin Console
- API user creation

### Process Flow

```
HRIS Event: New Employee Created
            │
            ▼
┌─────────────────────────────────────┐
│ 1. Validate Required Attributes     │
│    • Email, Name, Department        │
│    • Manager, Start Date            │
└─────────────────────────────────────┘
            │
            ▼
┌─────────────────────────────────────┐
│ 2. Determine Access Profile (RBAC)  │
│    • Department → Groups            │
│    • Title → Role Permissions       │
│    • Location → Regional Access     │
└─────────────────────────────────────┘
            │
            ▼
┌─────────────────────────────────────┐
│ 3. Activate User Account            │
│    • Send activation email          │
│    • Set temporary password         │
└─────────────────────────────────────┘
            │
            ▼
┌─────────────────────────────────────┐
│ 4. Provision Group Memberships      │
│    • All Employees                  │
│    • Department Group               │
│    • Role-based Groups              │
│    • Location Group                 │
└─────────────────────────────────────┘
            │
            ▼
┌─────────────────────────────────────┐
│ 5. Assign Applications              │
│    • Core Apps (Email, Slack, etc.) │
│    • Department-specific Apps       │
│    • Role-specific Apps             │
└─────────────────────────────────────┘
            │
            ▼
┌─────────────────────────────────────┐
│ 6. Enroll in MFA                    │
│    • Okta Verify (push)             │
│    • WebAuthn/Passkeys              │
│    • 7-day grace period             │
└─────────────────────────────────────┘
            │
            ▼
┌─────────────────────────────────────┐
│ 7. Provision Downstream Systems     │
│    • Active Directory               │
│    • Google Workspace               │
│    • Slack                          │
└─────────────────────────────────────┘
            │
            ▼
┌─────────────────────────────────────┐
│ 8. Create Tasks & Notifications     │
│    • Manager checklist              │
│    • 30-day access review           │
│    • Welcome email                  │
└─────────────────────────────────────┘
            │
            ▼
┌─────────────────────────────────────┐
│ 9. Audit & SIEM Logging             │
│    • Complete audit trail           │
│    • SIEM event forwarding          │
└─────────────────────────────────────┘
```

### Role-Based Access Control (RBAC) Matrix

| Department | Base Groups | Applications | Special Access |
|------------|-------------|--------------|----------------|
| Engineering | Eng_All, Eng_{Team} | GitHub, Jira, AWS | Production access (senior only) |
| Sales | Sales_All, Sales_{Region} | Salesforce, HubSpot | CRM admin (managers only) |
| Finance | Finance_All | NetSuite, Expensify | AP/AR based on role |
| HR | HR_All | Workday, BambooHR | PII access (limited) |
| IT | IT_All, IT_{Specialty} | All admin consoles | Elevated privileges |

---

## Mover Workflow (Department Transfer)

### Trigger Events
- HRIS department attribute change
- HRIS title attribute change
- HRIS manager attribute change

### Process Flow

```
HRIS Event: Department/Title Changed
            │
            ▼
┌─────────────────────────────────────┐
│ 1. Capture Change Details           │
│    • Previous values                │
│    • New values                     │
│    • Change timestamp               │
└─────────────────────────────────────┘
            │
            ▼
┌─────────────────────────────────────┐
│ 2. Calculate Access Delta           │
│    • Groups to remove               │
│    • Groups to add                  │
│    • Apps to remove                 │
│    • Apps to add                    │
└─────────────────────────────────────┘
            │
            ▼
┌─────────────────────────────────────┐
│ 3. Remove Old Access                │
│    • Previous department groups     │
│    • Previous role groups           │
│    • Previous department apps       │
└─────────────────────────────────────┘
            │
            ▼
┌─────────────────────────────────────┐
│ 4. Grant New Access                 │
│    • New department groups          │
│    • New role groups                │
│    • New department apps            │
└─────────────────────────────────────┘
            │
            ▼
┌─────────────────────────────────────┐
│ 5. Update Manager Assignment        │
│    • Update profile                 │
│    • Update reporting chain         │
└─────────────────────────────────────┘
            │
            ▼
┌─────────────────────────────────────┐
│ 6. Schedule Access Review           │
│    • 30-day review for new manager  │
│    • Verify appropriate access      │
└─────────────────────────────────────┘
            │
            ▼
┌─────────────────────────────────────┐
│ 7. Notifications                    │
│    • Previous manager               │
│    • New manager                    │
│    • Employee                       │
└─────────────────────────────────────┘
            │
            ▼
┌─────────────────────────────────────┐
│ 8. Audit & SIEM Logging             │
│    • Complete change trail          │
│    • SIEM event forwarding          │
└─────────────────────────────────────┘
```

### Access Delta Calculation

The mover workflow intelligently calculates what access should change:

```
Previous Access: Engineering Groups + Apps
New Access: Product Groups + Apps

Delta Calculation:
├── Groups to Remove: Eng_All, Eng_Backend, Eng_Platform
├── Groups to Keep: All_Employees, Office_Seattle
├── Groups to Add: Product_All, Product_Managers
├── Apps to Remove: AWS Console, GitHub Admin
├── Apps to Keep: Slack, Gmail, Jira
└── Apps to Add: ProductBoard, Amplitude, Figma
```

---

## Leaver Workflow (Offboarding)

### Trigger Events
- HRIS termination event
- Manual deactivation request
- Security-initiated immediate termination

### Termination Types

| Type | SLA | Session Revocation | Compliance Hold |
|------|-----|-------------------|-----------------|
| Voluntary | End of day | Graceful | Optional |
| Involuntary | Immediate | Immediate | Required |
| Security Concern | Immediate | Immediate + Token Revoke | Required |
| Contractor End | End of contract | Graceful | Optional |

### Process Flow

```
Termination Request Received
            │
            ▼
┌─────────────────────────────────────┐
│ 1. Validate & Approve               │
│    • Manager approval               │
│    • HR approval                    │
│    • Security approval (if needed)  │
└─────────────────────────────────────┘
            │
            ▼
┌─────────────────────────────────────┐
│ 2. Capture Pre-Offboarding State    │
│    • All group memberships          │
│    • All app assignments            │
│    • All MFA factors                │
│    • All active sessions            │
└─────────────────────────────────────┘
            │
            ▼
┌─────────────────────────────────────┐
│ 3. Revoke Active Sessions           │
│    • Kill all Okta sessions         │
│    • Revoke OAuth tokens            │
│    • Revoke refresh tokens          │
└─────────────────────────────────────┘
            │
            ▼
┌─────────────────────────────────────┐
│ 4. Remove Access                    │
│    • Remove from all groups         │
│    • Unassign all applications      │
│    • Reset all MFA factors          │
│    • Deregister all devices         │
└─────────────────────────────────────┘
            │
            ▼
┌─────────────────────────────────────┐
│ 5. Apply Compliance Hold            │
│    • Add to Compliance_Hold group   │
│    • Set retention metadata         │
│    • Schedule deletion job          │
└─────────────────────────────────────┘
            │
            ▼
┌─────────────────────────────────────┐
│ 6. Deactivate Account               │
│    • Set status to DEPROVISIONED    │
│    • Update offboarding metadata    │
└─────────────────────────────────────┘
            │
            ▼
┌─────────────────────────────────────┐
│ 7. Trigger Downstream Revocation    │
│    • Active Directory disable       │
│    • Google Workspace suspend       │
│    • Slack deactivate               │
│    • GitHub remove                  │
└─────────────────────────────────────┘
            │
            ▼
┌─────────────────────────────────────┐
│ 8. Generate Offboarding Report      │
│    • Access removed summary         │
│    • Compliance documentation       │
│    • Audit evidence package         │
└─────────────────────────────────────┘
            │
            ▼
┌─────────────────────────────────────┐
│ 9. Notifications                    │
│    • Manager                        │
│    • HR Team                        │
│    • Security Team (if applicable)  │
│    • IT Team                        │
└─────────────────────────────────────┘
            │
            ▼
┌─────────────────────────────────────┐
│ 10. Audit & SIEM Logging            │
│    • Complete offboarding trail     │
│    • SIEM high-priority event       │
└─────────────────────────────────────┘
```

---

## Compliance Framework Alignment

### SOC 2 Control Mappings

| Control | JML Implementation |
|---------|-------------------|
| CC6.1 - Logical Access | RBAC provisioning, group-based access |
| CC6.2 - Access Removal | Automated offboarding, session revocation |
| CC6.3 - Access Review | 30-day new hire review, quarterly campaigns |
| CC6.7 - Termination | Immediate access revocation, compliance hold |

### ISO 27001 Control Mappings

| Control | JML Implementation |
|---------|-------------------|
| A.9.2.1 - User Registration | Validated onboarding with HRIS source |
| A.9.2.2 - Access Provisioning | RBAC-based application assignment |
| A.9.2.5 - Access Rights Review | Scheduled reviews, transfer audits |
| A.9.2.6 - Access Removal | Comprehensive offboarding workflow |

### NIST 800-53 Control Mappings

| Control | JML Implementation |
|---------|-------------------|
| AC-2 - Account Management | Full lifecycle automation |
| AC-3 - Access Enforcement | Policy-based provisioning |
| AC-6 - Least Privilege | Role-based access profiles |
| PS-4 - Personnel Termination | Immediate revocation workflows |

### GDPR Considerations

| Requirement | JML Implementation |
|-------------|-------------------|
| Right to Erasure | Scheduled deletion after retention |
| Data Minimization | Only required access provisioned |
| Audit Trail | Complete logging for DPA requests |

---

## Metrics & SLAs

### Onboarding SLA

| Metric | Target | Measurement |
|--------|--------|-------------|
| Time to provision | < 3 minutes | Workflow duration |
| Account activation | < 5 minutes | First login capability |
| All apps accessible | < 10 minutes | Including downstream sync |

### Offboarding SLA

| Metric | Target | Measurement |
|--------|--------|-------------|
| Session revocation | < 30 seconds | Immediate for security |
| Access removal | < 2 minutes | All groups and apps |
| Downstream sync | < 5 minutes | AD, Google, Slack |

### Transfer SLA

| Metric | Target | Measurement |
|--------|--------|-------------|
| Access recalculation | < 1 minute | Delta computation |
| Access update | < 3 minutes | Remove old, add new |
| Manager notification | Immediate | Email sent |

---

## Error Handling & Escalation

### Retry Strategy

| Workflow | Retry Attempts | Delay | Escalation |
|----------|---------------|-------|------------|
| Joiner | 3 | 60 seconds | Create incident |
| Mover | 3 | 60 seconds | Rollback + incident |
| Leaver | 2 | 30 seconds | P1 incident (security) |

### Escalation Paths

```
Workflow Failure
      │
      ├── Retry 1-3 times
      │
      ▼
┌──────────────┐
│ Still Failed │
└──────────────┘
      │
      ├── Joiner: Create incident, notify HR + IT
      │
      ├── Mover: Rollback changes, create incident
      │
      └── Leaver: P1 incident, page on-call security
```

---

## Testing & Validation

### Test Scenarios

1. **Joiner Tests**
   - New employee from each department
   - Contractor with limited access
   - Executive with elevated access
   - Remote employee with location restrictions

2. **Mover Tests**
   - Same department, new role
   - Different department, same level
   - Promotion with elevated access
   - Demotion with access reduction

3. **Leaver Tests**
   - Voluntary resignation
   - Involuntary termination
   - Security-initiated immediate term
   - Contractor contract end

---

## Integration Points

### HRIS Systems Supported

- Workday (SCIM 2.0)
- BambooHR (API + Webhooks)
- Rippling (SCIM 2.0)
- ADP (API)
- UKG (API)

### Downstream Systems

- Active Directory (LDAP/SCIM)
- Google Workspace (Directory API)
- Slack (SCIM + API)
- AWS IAM Identity Center
- GitHub Enterprise (SCIM)
- Salesforce (SCIM)

---

## Author & Maintenance

**Author:** Mike Dominic
**Created:** December 2025
**Last Updated:** December 2025

This implementation demonstrates enterprise-grade identity lifecycle management aligned with Chainguard's IT Engineer (Identity/IAM) role requirements, specifically:
- Identity lifecycle automation using Okta Workflows
- HRIS integrations for authoritative source sync
- Zero Trust architecture principles
- Compliance framework alignment (SOC 2, ISO 27001, NIST, GDPR)
