# Access Certification Module

> **Chainguard Relevance:** This module demonstrates "quarterly access reviews, segregation-of-duties assessments, and role-attestation processes" - key requirements for the IT Engineer (Identity/IAM) role.

## Overview

The Access Certification module provides enterprise-grade access review capabilities for compliance with SOC 2, ISO 27001, NIST, and other regulatory frameworks. It enables:

- **Quarterly Access Reviews** - Regular certification of user access by managers
- **Segregation of Duties (SoD)** - Detection and remediation of conflicting privileges
- **Role Attestation** - Validation of role definitions and assignments
- **Compliance Reporting** - Audit evidence generation for external auditors

## Features

### Campaign Management

| Feature | Description |
|---------|-------------|
| Campaign Creation | Create quarterly, SoD, or role attestation campaigns |
| Reviewer Assignment | Assign managers, app owners, or security reviewers |
| Decision Tracking | Record approve, revoke, modify, or delegate decisions |
| Progress Monitoring | Real-time completion tracking and overdue alerts |
| Auto-Escalation | Automatic escalation for pending reviews |

### Compliance Reporting

| Framework | Controls Covered |
|-----------|-----------------|
| SOC 2 | CC6.1, CC6.2, CC6.3 |
| ISO 27001 | A.9.2.1, A.9.2.5 |
| NIST 800-53 | AC-2 |

### Risk Assessment

- Critical access identification
- High-risk item flagging
- SoD conflict detection
- Unused access identification

## Quick Start

### 1. Create a Campaign

```python
from campaign import CampaignManager, CampaignType
from datetime import date, timedelta

manager = CampaignManager()

# Create quarterly review campaign
campaign = manager.create_campaign(
    name="Q4 2025 Access Certification",
    campaign_type=CampaignType.QUARTERLY_REVIEW,
    created_by="admin@example.com",
    scheduled_start=date(2025, 10, 1),
    scheduled_end=date(2025, 10, 31),
    target_departments=["Engineering", "Finance", "Sales"],
    compliance_frameworks=["SOC2", "ISO27001"]
)
```

### 2. Add Access Items

```python
from campaign import AccessItem, RiskLevel

items = [
    AccessItem(
        user_id="user-001",
        user_email="john.doe@example.com",
        user_name="John Doe",
        department="Engineering",
        access_type="application",
        access_id="app-github",
        access_name="GitHub Enterprise",
        risk_level=RiskLevel.HIGH,
        is_privileged=True
    ),
    # ... more items
]

manager.add_access_items(campaign.id, items)
```

### 3. Start Campaign

```python
manager.start_campaign(campaign.id)
```

### 4. Record Decisions

```python
from campaign import ReviewDecision

manager.record_decision(
    campaign_id=campaign.id,
    item_id=items[0].id,
    decision=ReviewDecision.APPROVE,
    reviewer_id="manager@example.com",
    comment="Access appropriate for role"
)
```

### 5. Generate Compliance Report

```python
from reports import ComplianceReportGenerator, ComplianceFramework

generator = ComplianceReportGenerator()

evidence = generator.generate_campaign_evidence(
    campaign_data=campaign.dict(),
    generated_by="admin@example.com",
    frameworks=[ComplianceFramework.SOC2, ComplianceFramework.ISO27001]
)

# Export to markdown for auditors
markdown_report = generator.export_to_markdown(evidence)
```

## Campaign Types

### Quarterly Review
Standard manager certification of direct reports' access. Required for SOC 2 CC6.2 and ISO 27001 A.9.2.5.

```python
from campaign import create_quarterly_campaign

campaign = create_quarterly_campaign(
    manager=manager,
    quarter="Q4",
    year=2025,
    created_by="admin@example.com"
)
```

### Segregation of Duties Review
Identify and remediate SoD conflicts (e.g., user with both "Create PO" and "Approve PO" access).

```python
from campaign import create_sod_review_campaign

campaign = create_sod_review_campaign(
    manager=manager,
    created_by="admin@example.com",
    high_risk_only=True
)
```

### Role Attestation
Validate that role definitions and assignments follow least privilege principles.

```python
from campaign import create_role_attestation_campaign

campaign = create_role_attestation_campaign(
    manager=manager,
    created_by="admin@example.com",
    target_roles=["Admin", "Developer", "Finance_Approver"]
)
```

## Compliance Control Mappings

### SOC 2 Trust Services Criteria

| Control | Campaign Type | Evidence Generated |
|---------|---------------|-------------------|
| CC6.1 - Logical Access Security | All | Certification completion report |
| CC6.2 - Access Provisioning | Quarterly Review | Manager certifications |
| CC6.3 - Access Removal | All | Revocation decisions and actions |

### ISO 27001 Annex A

| Control | Campaign Type | Evidence Generated |
|---------|---------------|-------------------|
| A.9.2.1 - User Registration | Quarterly Review | Access certification records |
| A.9.2.5 - Review of Access Rights | Quarterly Review | Quarterly campaign completion |

### NIST 800-53

| Control | Campaign Type | Evidence Generated |
|---------|---------------|-------------------|
| AC-2 - Account Management | All | Full certification lifecycle |

## Audit Evidence Package

Generate a complete audit evidence package for external auditors:

```python
from reports import generate_audit_package, ComplianceFramework
from datetime import date

package = generate_audit_package(
    campaigns=[campaign1.dict(), campaign2.dict()],
    audit_period_start=date(2025, 1, 1),
    audit_period_end=date(2025, 12, 31),
    generated_by="iam-team@example.com",
    frameworks=[ComplianceFramework.SOC2, ComplianceFramework.ISO27001]
)

# Package includes:
# - Executive summary
# - Campaign evidence for each campaign
# - Control mappings
# - Attestation fields for sign-off
```

## Integration Points

### Okta Integration

- Pull user and group data via Okta API
- Trigger campaigns based on Okta events
- Execute revocations through Okta provisioning

### ServiceNow Integration

- Create review tasks for managers
- Track certification workflow
- Escalate overdue reviews

### Splunk SIEM

- Forward certification events for monitoring
- Alert on unusual certification patterns
- Dashboard for compliance status

## Best Practices

1. **Campaign Timing** - Run quarterly reviews during low-activity periods
2. **Reviewer Training** - Educate managers on certification responsibilities
3. **Risk-Based Focus** - Prioritize critical and high-risk access
4. **Automation** - Auto-revoke uncertified access after grace period
5. **Evidence Retention** - Maintain records for audit retention period (7 years)

## Files

| File | Description |
|------|-------------|
| `campaign.py` | Campaign management and workflow |
| `reports.py` | Compliance reports and audit evidence |
| `README.md` | This documentation |

## Author

**Mike Dominic** - December 2025

This module demonstrates enterprise access certification capabilities aligned with Chainguard IT Engineer (Identity/IAM) requirements for quarterly access reviews, segregation-of-duties assessments, and compliance reporting.
