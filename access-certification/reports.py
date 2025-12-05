"""
Access Certification Compliance Reports

This module generates compliance reports and audit evidence for access
certification campaigns.

Chainguard Relevance: Demonstrates compliance reporting and audit evidence
generation required for IT Engineer (Identity/IAM) role - specifically
"preparing evidence for SOC 2, ISO27001, and other regulatory audits."
"""

from datetime import datetime, date
from typing import List, Dict, Any, Optional
from enum import Enum
from pydantic import BaseModel, Field
import json


# =============================================================================
# REPORT MODELS
# =============================================================================

class ReportFormat(str, Enum):
    """Output formats for reports"""
    JSON = "json"
    MARKDOWN = "markdown"
    HTML = "html"
    CSV = "csv"
    PDF = "pdf"


class ComplianceFramework(str, Enum):
    """Supported compliance frameworks"""
    SOC2 = "SOC2"
    ISO27001 = "ISO27001"
    NIST = "NIST"
    HIPAA = "HIPAA"
    PCI_DSS = "PCI_DSS"
    GDPR = "GDPR"


class ControlMapping(BaseModel):
    """Maps campaign activities to compliance controls"""
    framework: ComplianceFramework
    control_id: str
    control_name: str
    description: str
    evidence_type: str
    satisfied: bool
    evidence_reference: Optional[str] = None


class CampaignEvidence(BaseModel):
    """Audit evidence for a certification campaign"""
    campaign_id: str
    campaign_name: str
    generated_at: datetime = Field(default_factory=datetime.utcnow)
    generated_by: str

    # Campaign details
    campaign_type: str
    start_date: date
    end_date: date
    duration_days: int

    # Statistics
    total_access_items: int
    certified_items: int
    revoked_items: int
    completion_rate: float

    # Risk metrics
    critical_items_reviewed: int
    high_risk_items_reviewed: int
    sod_conflicts_identified: int
    sod_conflicts_remediated: int

    # Reviewer metrics
    total_reviewers: int
    reviewers_completed: int
    average_review_time_hours: float

    # Compliance mappings
    control_mappings: List[ControlMapping] = Field(default_factory=list)

    # Audit trail
    audit_events: List[Dict[str, Any]] = Field(default_factory=list)


class ExecutiveSummary(BaseModel):
    """Executive summary for leadership reporting"""
    report_date: date
    reporting_period: str
    generated_by: str

    # Overview
    total_campaigns: int
    completed_campaigns: int
    active_campaigns: int

    # Access metrics
    total_users_reviewed: int
    total_access_items_reviewed: int
    items_certified: int
    items_revoked: int
    overall_certification_rate: float

    # Risk posture
    critical_risks_identified: int
    critical_risks_remediated: int
    sod_conflicts_total: int
    sod_conflicts_resolved: int

    # Compliance status
    frameworks_covered: List[str]
    controls_satisfied: int
    controls_total: int
    compliance_score: float

    # Recommendations
    key_findings: List[str]
    recommendations: List[str]


# =============================================================================
# CONTROL MAPPINGS
# =============================================================================

# SOC 2 Control Mappings
SOC2_CONTROLS = {
    "CC6.1": ControlMapping(
        framework=ComplianceFramework.SOC2,
        control_id="CC6.1",
        control_name="Logical Access Security",
        description="The entity implements logical access security software, "
                    "infrastructure, and architectures over protected information assets.",
        evidence_type="Access certification campaign completion report",
        satisfied=False
    ),
    "CC6.2": ControlMapping(
        framework=ComplianceFramework.SOC2,
        control_id="CC6.2",
        control_name="Access Provisioning",
        description="Prior to issuing system credentials and granting system access, "
                    "the entity registers and authorizes new internal and external users.",
        evidence_type="Manager certification of access assignments",
        satisfied=False
    ),
    "CC6.3": ControlMapping(
        framework=ComplianceFramework.SOC2,
        control_id="CC6.3",
        control_name="Access Removal",
        description="The entity removes access to protected information assets "
                    "when no longer required.",
        evidence_type="Revocation decisions and completion evidence",
        satisfied=False
    ),
}

# ISO 27001 Control Mappings
ISO27001_CONTROLS = {
    "A.9.2.1": ControlMapping(
        framework=ComplianceFramework.ISO27001,
        control_id="A.9.2.1",
        control_name="User Registration and De-registration",
        description="A formal user registration and de-registration process shall be "
                    "implemented to enable assignment of access rights.",
        evidence_type="Access certification records",
        satisfied=False
    ),
    "A.9.2.5": ControlMapping(
        framework=ComplianceFramework.ISO27001,
        control_id="A.9.2.5",
        control_name="Review of User Access Rights",
        description="Asset owners shall review users' access rights at regular intervals.",
        evidence_type="Quarterly access certification campaign report",
        satisfied=False
    ),
}

# NIST Control Mappings
NIST_CONTROLS = {
    "AC-2": ControlMapping(
        framework=ComplianceFramework.NIST,
        control_id="AC-2",
        control_name="Account Management",
        description="The organization manages information system accounts, including "
                    "establishing, activating, modifying, reviewing, disabling, and removing accounts.",
        evidence_type="Access certification with remediation actions",
        satisfied=False
    ),
}


# =============================================================================
# REPORT GENERATORS
# =============================================================================

class ComplianceReportGenerator:
    """Generates compliance reports for access certification campaigns"""

    def __init__(self):
        self.control_mappings = {
            ComplianceFramework.SOC2: SOC2_CONTROLS,
            ComplianceFramework.ISO27001: ISO27001_CONTROLS,
            ComplianceFramework.NIST: NIST_CONTROLS,
        }

    def generate_campaign_evidence(
        self,
        campaign_data: Dict[str, Any],
        generated_by: str,
        frameworks: List[ComplianceFramework] = None
    ) -> CampaignEvidence:
        """Generate audit evidence for a certification campaign"""

        frameworks = frameworks or [
            ComplianceFramework.SOC2,
            ComplianceFramework.ISO27001
        ]

        # Calculate duration
        start = campaign_data.get("scheduled_start")
        end = campaign_data.get("actual_end") or campaign_data.get("scheduled_end")
        duration = (end - start).days if start and end else 0

        # Calculate completion rate
        total = campaign_data.get("total_items", 0)
        certified = campaign_data.get("certified_items", 0)
        revoked = campaign_data.get("revoked_items", 0)
        completion_rate = ((certified + revoked) / total * 100) if total > 0 else 0

        # Get control mappings
        mappings = []
        for framework in frameworks:
            framework_controls = self.control_mappings.get(framework, {})
            for control in framework_controls.values():
                control_copy = control.copy()
                control_copy.satisfied = completion_rate >= 95  # 95% threshold
                control_copy.evidence_reference = f"Campaign-{campaign_data.get('id')}"
                mappings.append(control_copy)

        return CampaignEvidence(
            campaign_id=campaign_data.get("id", "unknown"),
            campaign_name=campaign_data.get("name", "Unknown Campaign"),
            generated_by=generated_by,
            campaign_type=campaign_data.get("campaign_type", "unknown"),
            start_date=start,
            end_date=end,
            duration_days=duration,
            total_access_items=total,
            certified_items=certified,
            revoked_items=revoked,
            completion_rate=completion_rate,
            critical_items_reviewed=campaign_data.get("critical_items", 0),
            high_risk_items_reviewed=campaign_data.get("high_risk_items", 0),
            sod_conflicts_identified=campaign_data.get("sod_conflicts_found", 0),
            sod_conflicts_remediated=campaign_data.get("sod_conflicts_resolved", 0),
            total_reviewers=campaign_data.get("total_reviewers", 0),
            reviewers_completed=campaign_data.get("reviewers_completed", 0),
            average_review_time_hours=campaign_data.get("avg_review_time", 0),
            control_mappings=mappings,
            audit_events=campaign_data.get("audit_events", [])
        )

    def generate_executive_summary(
        self,
        campaigns: List[Dict[str, Any]],
        reporting_period: str,
        generated_by: str
    ) -> ExecutiveSummary:
        """Generate executive summary across multiple campaigns"""

        # Aggregate metrics
        total_campaigns = len(campaigns)
        completed = sum(1 for c in campaigns if c.get("status") == "completed")
        active = sum(1 for c in campaigns if c.get("status") == "active")

        total_items = sum(c.get("total_items", 0) for c in campaigns)
        certified = sum(c.get("certified_items", 0) for c in campaigns)
        revoked = sum(c.get("revoked_items", 0) for c in campaigns)

        # Unique users
        users = set()
        for c in campaigns:
            users.update(c.get("user_ids", []))

        # Risk metrics
        critical_identified = sum(c.get("critical_items", 0) for c in campaigns)
        critical_remediated = sum(c.get("critical_remediated", 0) for c in campaigns)
        sod_total = sum(c.get("sod_conflicts_found", 0) for c in campaigns)
        sod_resolved = sum(c.get("sod_conflicts_resolved", 0) for c in campaigns)

        # Compliance score
        controls_satisfied = 0
        controls_total = 0
        for c in campaigns:
            for mapping in c.get("control_mappings", []):
                controls_total += 1
                if mapping.get("satisfied"):
                    controls_satisfied += 1

        compliance_score = (controls_satisfied / controls_total * 100) if controls_total > 0 else 0

        # Generate recommendations
        recommendations = []
        if revoked / total_items > 0.1 if total_items > 0 else False:
            recommendations.append(
                "High revocation rate (>10%) indicates need for improved provisioning controls"
            )
        if sod_total > 0 and sod_resolved < sod_total:
            recommendations.append(
                f"{sod_total - sod_resolved} SoD conflicts require remediation"
            )
        if active > completed:
            recommendations.append(
                "Multiple active campaigns - consider staggering to reduce reviewer fatigue"
            )

        return ExecutiveSummary(
            report_date=date.today(),
            reporting_period=reporting_period,
            generated_by=generated_by,
            total_campaigns=total_campaigns,
            completed_campaigns=completed,
            active_campaigns=active,
            total_users_reviewed=len(users),
            total_access_items_reviewed=total_items,
            items_certified=certified,
            items_revoked=revoked,
            overall_certification_rate=(certified / total_items * 100) if total_items > 0 else 0,
            critical_risks_identified=critical_identified,
            critical_risks_remediated=critical_remediated,
            sod_conflicts_total=sod_total,
            sod_conflicts_resolved=sod_resolved,
            frameworks_covered=["SOC2", "ISO27001", "NIST"],
            controls_satisfied=controls_satisfied,
            controls_total=controls_total,
            compliance_score=compliance_score,
            key_findings=[
                f"Reviewed {total_items} access items across {total_campaigns} campaigns",
                f"Certification rate: {(certified / total_items * 100):.1f}%" if total_items > 0 else "No items reviewed",
                f"Revocation rate: {(revoked / total_items * 100):.1f}%" if total_items > 0 else "No items reviewed",
            ],
            recommendations=recommendations
        )

    def export_to_markdown(
        self,
        evidence: CampaignEvidence,
        include_audit_trail: bool = True
    ) -> str:
        """Export campaign evidence to markdown format"""

        md = f"""# Access Certification Campaign Evidence

## Campaign Details

| Field | Value |
|-------|-------|
| Campaign ID | {evidence.campaign_id} |
| Campaign Name | {evidence.campaign_name} |
| Campaign Type | {evidence.campaign_type} |
| Start Date | {evidence.start_date} |
| End Date | {evidence.end_date} |
| Duration | {evidence.duration_days} days |
| Generated At | {evidence.generated_at.isoformat()} |
| Generated By | {evidence.generated_by} |

## Certification Metrics

| Metric | Value |
|--------|-------|
| Total Access Items | {evidence.total_access_items} |
| Items Certified | {evidence.certified_items} |
| Items Revoked | {evidence.revoked_items} |
| Completion Rate | {evidence.completion_rate:.1f}% |

## Risk Metrics

| Metric | Value |
|--------|-------|
| Critical Items Reviewed | {evidence.critical_items_reviewed} |
| High Risk Items Reviewed | {evidence.high_risk_items_reviewed} |
| SoD Conflicts Identified | {evidence.sod_conflicts_identified} |
| SoD Conflicts Remediated | {evidence.sod_conflicts_remediated} |

## Reviewer Metrics

| Metric | Value |
|--------|-------|
| Total Reviewers | {evidence.total_reviewers} |
| Reviewers Completed | {evidence.reviewers_completed} |
| Average Review Time | {evidence.average_review_time_hours:.1f} hours |

## Compliance Control Mappings

| Framework | Control ID | Control Name | Satisfied |
|-----------|------------|--------------|-----------|
"""
        for mapping in evidence.control_mappings:
            status = "Yes" if mapping.satisfied else "No"
            md += f"| {mapping.framework.value} | {mapping.control_id} | {mapping.control_name} | {status} |\n"

        if include_audit_trail and evidence.audit_events:
            md += "\n## Audit Trail\n\n"
            md += "| Timestamp | Event | User | Details |\n"
            md += "|-----------|-------|------|--------|\n"
            for event in evidence.audit_events[-20:]:  # Last 20 events
                md += f"| {event.get('timestamp', 'N/A')} | {event.get('event', 'N/A')} | {event.get('user', 'N/A')} | {event.get('details', 'N/A')} |\n"

        md += f"""
---

*This report was generated for compliance audit purposes.*
*Chainguard IT Engineer (Identity/IAM) Portfolio - Mike Dominic*
"""

        return md

    def export_to_json(self, evidence: CampaignEvidence) -> str:
        """Export campaign evidence to JSON format"""
        return evidence.json(indent=2)


# =============================================================================
# AUDIT EVIDENCE PACKAGE
# =============================================================================

class AuditEvidencePackage(BaseModel):
    """Complete audit evidence package for external auditors"""
    package_id: str = Field(default_factory=lambda: f"AEP-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}")
    generated_at: datetime = Field(default_factory=datetime.utcnow)
    generated_by: str
    audit_period_start: date
    audit_period_end: date

    # Contents
    executive_summary: Optional[ExecutiveSummary] = None
    campaign_evidence: List[CampaignEvidence] = Field(default_factory=list)

    # Attestations
    iam_team_attestation: Optional[str] = None
    security_team_attestation: Optional[str] = None
    management_attestation: Optional[str] = None

    # Metadata
    frameworks: List[str] = Field(default_factory=list)
    controls_covered: int = 0
    controls_satisfied: int = 0


def generate_audit_package(
    campaigns: List[Dict[str, Any]],
    audit_period_start: date,
    audit_period_end: date,
    generated_by: str,
    frameworks: List[ComplianceFramework] = None
) -> AuditEvidencePackage:
    """
    Generate a complete audit evidence package

    This implements the "preparing evidence for SOC 2, ISO27001" requirement.
    """

    generator = ComplianceReportGenerator()
    frameworks = frameworks or [ComplianceFramework.SOC2, ComplianceFramework.ISO27001]

    # Generate evidence for each campaign
    campaign_evidence = []
    for campaign in campaigns:
        evidence = generator.generate_campaign_evidence(
            campaign,
            generated_by,
            frameworks
        )
        campaign_evidence.append(evidence)

    # Generate executive summary
    period = f"{audit_period_start.strftime('%B %d, %Y')} - {audit_period_end.strftime('%B %d, %Y')}"
    summary = generator.generate_executive_summary(
        campaigns,
        period,
        generated_by
    )

    return AuditEvidencePackage(
        generated_by=generated_by,
        audit_period_start=audit_period_start,
        audit_period_end=audit_period_end,
        executive_summary=summary,
        campaign_evidence=campaign_evidence,
        frameworks=[f.value for f in frameworks],
        controls_covered=summary.controls_total,
        controls_satisfied=summary.controls_satisfied
    )
