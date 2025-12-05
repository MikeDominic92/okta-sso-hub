"""
Access Certification Campaign Management

This module manages access certification campaigns for quarterly access reviews,
role attestation, and compliance validation.

Chainguard Relevance: Demonstrates "quarterly access reviews, segregation-of-duties
assessments, and role-attestation processes" required for IT Engineer (Identity/IAM) role.
"""

from datetime import datetime, date, timedelta
from typing import List, Optional, Dict, Any
from enum import Enum
from pydantic import BaseModel, Field
import uuid


# =============================================================================
# ENUMS
# =============================================================================

class CampaignStatus(str, Enum):
    """Campaign lifecycle status"""
    DRAFT = "draft"
    SCHEDULED = "scheduled"
    ACTIVE = "active"
    REVIEW = "review"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class CampaignType(str, Enum):
    """Types of access certification campaigns"""
    QUARTERLY_REVIEW = "quarterly_review"
    MANAGER_CERTIFICATION = "manager_certification"
    APPLICATION_ACCESS = "application_access"
    PRIVILEGED_ACCESS = "privileged_access"
    SOD_REVIEW = "sod_review"  # Segregation of Duties
    NEW_HIRE_30DAY = "new_hire_30day"
    ROLE_ATTESTATION = "role_attestation"
    COMPLIANCE_AUDIT = "compliance_audit"


class ReviewDecision(str, Enum):
    """Reviewer's decision on access"""
    APPROVE = "approve"
    REVOKE = "revoke"
    MODIFY = "modify"
    DELEGATE = "delegate"
    PENDING = "pending"


class RiskLevel(str, Enum):
    """Risk classification for access items"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


# =============================================================================
# MODELS
# =============================================================================

class AccessItem(BaseModel):
    """An individual access item to be reviewed"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    user_email: str
    user_name: str
    department: str

    # Access details
    access_type: str  # "group", "application", "role", "entitlement"
    access_id: str
    access_name: str
    access_description: Optional[str] = None

    # Risk and compliance
    risk_level: RiskLevel = RiskLevel.MEDIUM
    is_privileged: bool = False
    sod_conflicts: List[str] = Field(default_factory=list)

    # Review metadata
    granted_date: Optional[date] = None
    granted_by: Optional[str] = None
    last_used: Optional[datetime] = None
    usage_count_30d: int = 0

    # Decision
    decision: ReviewDecision = ReviewDecision.PENDING
    decision_by: Optional[str] = None
    decision_date: Optional[datetime] = None
    decision_comment: Optional[str] = None


class Reviewer(BaseModel):
    """A reviewer assigned to certify access"""
    id: str
    email: str
    name: str
    role: str  # "manager", "app_owner", "security", "delegate"
    items_assigned: int = 0
    items_completed: int = 0
    items_pending: int = 0


class Campaign(BaseModel):
    """Access certification campaign"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    description: Optional[str] = None
    campaign_type: CampaignType

    # Lifecycle
    status: CampaignStatus = CampaignStatus.DRAFT
    created_at: datetime = Field(default_factory=datetime.utcnow)
    created_by: str

    # Schedule
    scheduled_start: Optional[date] = None
    scheduled_end: Optional[date] = None
    actual_start: Optional[datetime] = None
    actual_end: Optional[datetime] = None

    # Scope
    target_users: List[str] = Field(default_factory=list)  # User IDs
    target_departments: List[str] = Field(default_factory=list)
    target_applications: List[str] = Field(default_factory=list)
    target_groups: List[str] = Field(default_factory=list)
    include_privileged_only: bool = False

    # Settings
    auto_revoke_uncertified: bool = False
    escalation_enabled: bool = True
    reminder_frequency_days: int = 7
    require_comments_for_revoke: bool = True
    require_comments_for_approve: bool = False

    # Progress
    total_items: int = 0
    certified_items: int = 0
    revoked_items: int = 0
    pending_items: int = 0

    # Compliance
    compliance_frameworks: List[str] = Field(default_factory=list)
    evidence_generated: bool = False

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat(),
            date: lambda v: v.isoformat()
        }

    @property
    def completion_percentage(self) -> float:
        if self.total_items == 0:
            return 0.0
        return round((self.certified_items + self.revoked_items) / self.total_items * 100, 2)

    @property
    def is_overdue(self) -> bool:
        if self.scheduled_end and self.status == CampaignStatus.ACTIVE:
            return date.today() > self.scheduled_end
        return False


class CampaignSummary(BaseModel):
    """Summary statistics for a campaign"""
    campaign_id: str
    campaign_name: str
    campaign_type: CampaignType
    status: CampaignStatus

    # Progress
    total_items: int
    certified_count: int
    revoked_count: int
    pending_count: int
    completion_percentage: float

    # Reviewers
    total_reviewers: int
    reviewers_completed: int

    # Risk breakdown
    critical_items: int
    high_risk_items: int
    sod_conflicts_found: int

    # Timeline
    days_remaining: Optional[int]
    is_overdue: bool


# =============================================================================
# CAMPAIGN MANAGER
# =============================================================================

class CampaignManager:
    """Manages access certification campaigns"""

    def __init__(self):
        self.campaigns: Dict[str, Campaign] = {}
        self.access_items: Dict[str, List[AccessItem]] = {}
        self.reviewers: Dict[str, List[Reviewer]] = {}

    def create_campaign(
        self,
        name: str,
        campaign_type: CampaignType,
        created_by: str,
        scheduled_start: date,
        scheduled_end: date,
        description: str = None,
        target_departments: List[str] = None,
        target_applications: List[str] = None,
        compliance_frameworks: List[str] = None
    ) -> Campaign:
        """Create a new access certification campaign"""

        campaign = Campaign(
            name=name,
            description=description,
            campaign_type=campaign_type,
            created_by=created_by,
            scheduled_start=scheduled_start,
            scheduled_end=scheduled_end,
            target_departments=target_departments or [],
            target_applications=target_applications or [],
            compliance_frameworks=compliance_frameworks or ["SOC2", "ISO27001"]
        )

        self.campaigns[campaign.id] = campaign
        self.access_items[campaign.id] = []
        self.reviewers[campaign.id] = []

        return campaign

    def add_access_items(
        self,
        campaign_id: str,
        items: List[AccessItem]
    ) -> int:
        """Add access items to a campaign for review"""

        if campaign_id not in self.campaigns:
            raise ValueError(f"Campaign {campaign_id} not found")

        self.access_items[campaign_id].extend(items)

        campaign = self.campaigns[campaign_id]
        campaign.total_items = len(self.access_items[campaign_id])
        campaign.pending_items = campaign.total_items

        return len(items)

    def assign_reviewer(
        self,
        campaign_id: str,
        reviewer: Reviewer,
        item_ids: List[str] = None
    ) -> int:
        """Assign a reviewer to a campaign"""

        if campaign_id not in self.campaigns:
            raise ValueError(f"Campaign {campaign_id} not found")

        # If no specific items, count all unassigned
        if item_ids is None:
            items = self.access_items.get(campaign_id, [])
            reviewer.items_assigned = len(items)
            reviewer.items_pending = len(items)
        else:
            reviewer.items_assigned = len(item_ids)
            reviewer.items_pending = len(item_ids)

        self.reviewers[campaign_id].append(reviewer)

        return reviewer.items_assigned

    def start_campaign(self, campaign_id: str) -> Campaign:
        """Start an access certification campaign"""

        if campaign_id not in self.campaigns:
            raise ValueError(f"Campaign {campaign_id} not found")

        campaign = self.campaigns[campaign_id]

        if campaign.status != CampaignStatus.DRAFT and campaign.status != CampaignStatus.SCHEDULED:
            raise ValueError(f"Campaign cannot be started from {campaign.status} status")

        campaign.status = CampaignStatus.ACTIVE
        campaign.actual_start = datetime.utcnow()

        return campaign

    def record_decision(
        self,
        campaign_id: str,
        item_id: str,
        decision: ReviewDecision,
        reviewer_id: str,
        comment: str = None
    ) -> AccessItem:
        """Record a certification decision for an access item"""

        if campaign_id not in self.campaigns:
            raise ValueError(f"Campaign {campaign_id} not found")

        items = self.access_items.get(campaign_id, [])
        item = next((i for i in items if i.id == item_id), None)

        if not item:
            raise ValueError(f"Access item {item_id} not found")

        item.decision = decision
        item.decision_by = reviewer_id
        item.decision_date = datetime.utcnow()
        item.decision_comment = comment

        # Update campaign stats
        campaign = self.campaigns[campaign_id]
        campaign.pending_items -= 1

        if decision == ReviewDecision.APPROVE:
            campaign.certified_items += 1
        elif decision == ReviewDecision.REVOKE:
            campaign.revoked_items += 1

        return item

    def get_campaign_summary(self, campaign_id: str) -> CampaignSummary:
        """Get summary statistics for a campaign"""

        if campaign_id not in self.campaigns:
            raise ValueError(f"Campaign {campaign_id} not found")

        campaign = self.campaigns[campaign_id]
        items = self.access_items.get(campaign_id, [])
        reviewers = self.reviewers.get(campaign_id, [])

        # Calculate risk breakdown
        critical_items = sum(1 for i in items if i.risk_level == RiskLevel.CRITICAL)
        high_risk_items = sum(1 for i in items if i.risk_level == RiskLevel.HIGH)
        sod_conflicts = sum(1 for i in items if len(i.sod_conflicts) > 0)

        # Calculate days remaining
        days_remaining = None
        if campaign.scheduled_end and campaign.status == CampaignStatus.ACTIVE:
            delta = campaign.scheduled_end - date.today()
            days_remaining = delta.days

        # Count completed reviewers
        reviewers_completed = sum(
            1 for r in reviewers
            if r.items_completed == r.items_assigned
        )

        return CampaignSummary(
            campaign_id=campaign.id,
            campaign_name=campaign.name,
            campaign_type=campaign.campaign_type,
            status=campaign.status,
            total_items=campaign.total_items,
            certified_count=campaign.certified_items,
            revoked_count=campaign.revoked_items,
            pending_count=campaign.pending_items,
            completion_percentage=campaign.completion_percentage,
            total_reviewers=len(reviewers),
            reviewers_completed=reviewers_completed,
            critical_items=critical_items,
            high_risk_items=high_risk_items,
            sod_conflicts_found=sod_conflicts,
            days_remaining=days_remaining,
            is_overdue=campaign.is_overdue
        )

    def complete_campaign(self, campaign_id: str) -> Campaign:
        """Complete an access certification campaign"""

        if campaign_id not in self.campaigns:
            raise ValueError(f"Campaign {campaign_id} not found")

        campaign = self.campaigns[campaign_id]
        campaign.status = CampaignStatus.COMPLETED
        campaign.actual_end = datetime.utcnow()

        return campaign

    def get_pending_reviews(
        self,
        campaign_id: str,
        reviewer_id: str
    ) -> List[AccessItem]:
        """Get pending access items for a reviewer"""

        items = self.access_items.get(campaign_id, [])
        return [i for i in items if i.decision == ReviewDecision.PENDING]

    def get_overdue_items(self, campaign_id: str) -> List[AccessItem]:
        """Get items that haven't been reviewed and campaign is overdue"""

        if campaign_id not in self.campaigns:
            raise ValueError(f"Campaign {campaign_id} not found")

        campaign = self.campaigns[campaign_id]

        if not campaign.is_overdue:
            return []

        items = self.access_items.get(campaign_id, [])
        return [i for i in items if i.decision == ReviewDecision.PENDING]


# =============================================================================
# QUARTERLY CAMPAIGN GENERATOR
# =============================================================================

def create_quarterly_campaign(
    manager: CampaignManager,
    quarter: str,  # "Q1", "Q2", "Q3", "Q4"
    year: int,
    created_by: str,
    departments: List[str] = None
) -> Campaign:
    """
    Create a standard quarterly access certification campaign

    This implements the "quarterly access reviews" requirement.
    """

    # Calculate quarter dates
    quarter_starts = {
        "Q1": date(year, 1, 1),
        "Q2": date(year, 4, 1),
        "Q3": date(year, 7, 1),
        "Q4": date(year, 10, 1),
    }
    quarter_ends = {
        "Q1": date(year, 1, 31),
        "Q2": date(year, 4, 30),
        "Q3": date(year, 7, 31),
        "Q4": date(year, 10, 31),
    }

    campaign = manager.create_campaign(
        name=f"{quarter} {year} Access Certification",
        campaign_type=CampaignType.QUARTERLY_REVIEW,
        created_by=created_by,
        scheduled_start=quarter_starts[quarter],
        scheduled_end=quarter_ends[quarter],
        description=f"Quarterly access certification for {quarter} {year}. "
                    f"All managers must certify their direct reports' access.",
        target_departments=departments or [],
        compliance_frameworks=["SOC2", "ISO27001", "NIST"]
    )

    return campaign


def create_sod_review_campaign(
    manager: CampaignManager,
    created_by: str,
    high_risk_only: bool = True
) -> Campaign:
    """
    Create a Segregation of Duties review campaign

    This implements the "segregation-of-duties assessments" requirement.
    """

    campaign = manager.create_campaign(
        name=f"SoD Review - {date.today().strftime('%B %Y')}",
        campaign_type=CampaignType.SOD_REVIEW,
        created_by=created_by,
        scheduled_start=date.today(),
        scheduled_end=date.today() + timedelta(days=14),
        description="Review and remediate segregation of duties conflicts. "
                    "Focus on users with conflicting privileged access.",
        compliance_frameworks=["SOC2", "ISO27001"]
    )

    return campaign


def create_role_attestation_campaign(
    manager: CampaignManager,
    created_by: str,
    target_roles: List[str]
) -> Campaign:
    """
    Create a role attestation campaign

    This implements the "role-attestation processes" requirement.
    """

    campaign = manager.create_campaign(
        name=f"Role Attestation - {date.today().strftime('%B %Y')}",
        campaign_type=CampaignType.ROLE_ATTESTATION,
        created_by=created_by,
        scheduled_start=date.today(),
        scheduled_end=date.today() + timedelta(days=21),
        description="Attest that role definitions are accurate and "
                    "role assignments follow least privilege principles.",
        compliance_frameworks=["SOC2", "ISO27001", "NIST"]
    )

    return campaign
