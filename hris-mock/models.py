"""
HRIS Data Models - Core data structures for identity lifecycle management

These models represent the canonical employee data structure used across
enterprise HRIS systems (Workday, BambooHR, Rippling, ADP, etc.)

Chainguard Relevance: Demonstrates understanding of enterprise HR data
structures required for IT Engineer (Identity/IAM) role.
"""

from pydantic import BaseModel, EmailStr, Field, validator
from typing import Optional, List, Dict, Any
from datetime import datetime, date
from enum import Enum
import uuid


# =============================================================================
# ENUMERATIONS
# =============================================================================

class EmploymentStatus(str, Enum):
    """Employee lifecycle status"""
    PENDING = "pending"           # Pre-hire, not yet started
    ACTIVE = "active"             # Currently employed
    ON_LEAVE = "on_leave"         # LOA, sabbatical, etc.
    SUSPENDED = "suspended"       # Temporary access suspension
    TERMINATED = "terminated"     # Employment ended


class EmploymentType(str, Enum):
    """Type of employment relationship"""
    FULL_TIME = "full_time"
    PART_TIME = "part_time"
    CONTRACTOR = "contractor"
    INTERN = "intern"
    TEMPORARY = "temporary"
    CONSULTANT = "consultant"


class TerminationType(str, Enum):
    """Reason for termination"""
    VOLUNTARY = "voluntary"               # Resignation
    INVOLUNTARY = "involuntary"           # Termination
    RETIREMENT = "retirement"
    CONTRACT_END = "contract_end"
    LAYOFF = "layoff"
    SECURITY_CONCERN = "security_concern" # Immediate termination
    DEATH = "death"
    MUTUAL_AGREEMENT = "mutual_agreement"


class WorkerType(str, Enum):
    """Classification for access provisioning"""
    EMPLOYEE = "employee"
    CONTINGENT = "contingent"
    VENDOR = "vendor"
    PARTNER = "partner"


class PayFrequency(str, Enum):
    """Payroll frequency"""
    WEEKLY = "weekly"
    BIWEEKLY = "biweekly"
    SEMIMONTHLY = "semimonthly"
    MONTHLY = "monthly"


# =============================================================================
# CORE EMPLOYEE MODELS
# =============================================================================

class Name(BaseModel):
    """Employee name components"""
    first_name: str
    last_name: str
    middle_name: Optional[str] = None
    preferred_name: Optional[str] = None
    suffix: Optional[str] = None
    title: Optional[str] = None  # Mr., Ms., Dr., etc.

    @property
    def display_name(self) -> str:
        if self.preferred_name:
            return f"{self.preferred_name} {self.last_name}"
        return f"{self.first_name} {self.last_name}"

    @property
    def full_name(self) -> str:
        parts = [self.first_name]
        if self.middle_name:
            parts.append(self.middle_name)
        parts.append(self.last_name)
        if self.suffix:
            parts.append(self.suffix)
        return " ".join(parts)


class ContactInfo(BaseModel):
    """Employee contact information"""
    work_email: EmailStr
    personal_email: Optional[EmailStr] = None
    work_phone: Optional[str] = None
    mobile_phone: Optional[str] = None
    home_phone: Optional[str] = None


class Address(BaseModel):
    """Physical address"""
    street_line_1: str
    street_line_2: Optional[str] = None
    city: str
    state: str
    postal_code: str
    country: str = "USA"


class Department(BaseModel):
    """Department/organization unit"""
    id: str
    name: str
    code: str
    parent_id: Optional[str] = None
    cost_center: Optional[str] = None
    manager_id: Optional[str] = None


class JobPosition(BaseModel):
    """Job/position information"""
    title: str
    job_code: Optional[str] = None
    job_family: Optional[str] = None
    job_level: Optional[str] = None
    is_manager: bool = False
    is_executive: bool = False


class Manager(BaseModel):
    """Manager/supervisor reference"""
    id: str
    employee_number: str
    email: EmailStr
    name: str


class Location(BaseModel):
    """Work location"""
    id: str
    name: str
    code: str
    address: Optional[Address] = None
    timezone: Optional[str] = None
    is_remote: bool = False


class Employment(BaseModel):
    """Employment details"""
    status: EmploymentStatus
    type: EmploymentType
    worker_type: WorkerType = WorkerType.EMPLOYEE
    hire_date: date
    original_hire_date: Optional[date] = None  # For rehires
    termination_date: Optional[date] = None
    termination_type: Optional[TerminationType] = None
    last_day_worked: Optional[date] = None
    pay_frequency: Optional[PayFrequency] = None
    fte: float = 1.0  # Full-time equivalent


class Compensation(BaseModel):
    """Compensation information (for access tiering)"""
    pay_grade: Optional[str] = None
    pay_band: Optional[str] = None
    is_exempt: bool = True  # FLSA exempt status


class SecurityClearance(BaseModel):
    """Security clearance for access control"""
    level: Optional[str] = None  # e.g., "confidential", "secret", "top_secret"
    granted_date: Optional[date] = None
    expiration_date: Optional[date] = None
    investigation_type: Optional[str] = None


# =============================================================================
# MAIN EMPLOYEE MODEL
# =============================================================================

class Employee(BaseModel):
    """
    Complete employee record matching enterprise HRIS schema

    This model consolidates all employee attributes needed for:
    - Identity provisioning (Okta, AD, etc.)
    - Access control decisions (RBAC)
    - Compliance reporting (SOC 2, etc.)
    """
    # Identifiers
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    employee_number: str
    external_id: Optional[str] = None  # For SCIM

    # Personal Information
    name: Name
    contact: ContactInfo
    work_address: Optional[Address] = None
    home_address: Optional[Address] = None

    # Organizational
    department: Department
    position: JobPosition
    manager: Optional[Manager] = None
    location: Location

    # Employment
    employment: Employment

    # Compensation (for access tiering)
    compensation: Optional[Compensation] = None

    # Security
    security_clearance: Optional[SecurityClearance] = None

    # Custom Attributes (for org-specific needs)
    custom_attributes: Dict[str, Any] = Field(default_factory=dict)

    # Metadata
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    created_by: Optional[str] = None
    updated_by: Optional[str] = None

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat(),
            date: lambda v: v.isoformat()
        }

    @property
    def email(self) -> str:
        return self.contact.work_email

    @property
    def display_name(self) -> str:
        return self.name.display_name

    @property
    def is_active(self) -> bool:
        return self.employment.status == EmploymentStatus.ACTIVE

    @property
    def is_manager(self) -> bool:
        return self.position.is_manager

    def to_okta_profile(self) -> Dict[str, Any]:
        """Convert to Okta user profile format"""
        return {
            "firstName": self.name.first_name,
            "lastName": self.name.last_name,
            "displayName": self.display_name,
            "email": self.email,
            "login": self.email,
            "employeeNumber": self.employee_number,
            "department": self.department.name,
            "title": self.position.title,
            "manager": self.manager.email if self.manager else None,
            "managerId": self.manager.id if self.manager else None,
            "costCenter": self.department.cost_center,
            "location": self.location.name,
            "startDate": self.employment.hire_date.isoformat(),
            "employeeType": self.employment.type.value,
            "workerType": self.employment.worker_type.value,
        }

    def to_scim_user(self) -> Dict[str, Any]:
        """Convert to SCIM 2.0 User format"""
        return {
            "schemas": [
                "urn:ietf:params:scim:schemas:core:2.0:User",
                "urn:ietf:params:scim:schemas:extension:enterprise:2.0:User"
            ],
            "id": self.id,
            "externalId": self.employee_number,
            "userName": self.email,
            "name": {
                "givenName": self.name.first_name,
                "familyName": self.name.last_name,
                "middleName": self.name.middle_name,
                "formatted": self.name.full_name
            },
            "displayName": self.display_name,
            "emails": [
                {"value": self.email, "type": "work", "primary": True}
            ],
            "phoneNumbers": [
                {"value": self.contact.work_phone, "type": "work"}
            ] if self.contact.work_phone else [],
            "active": self.is_active,
            "title": self.position.title,
            "urn:ietf:params:scim:schemas:extension:enterprise:2.0:User": {
                "employeeNumber": self.employee_number,
                "costCenter": self.department.cost_center,
                "organization": self.department.name,
                "division": self.department.parent_id,
                "department": self.department.name,
                "manager": {
                    "value": self.manager.id,
                    "$ref": f"/Users/{self.manager.id}",
                    "displayName": self.manager.name
                } if self.manager else None
            }
        }


# =============================================================================
# EVENT MODELS
# =============================================================================

class ChangeDetail(BaseModel):
    """Details of a field change"""
    field: str
    old_value: Any
    new_value: Any


class EmployeeEvent(BaseModel):
    """Event representing an employee lifecycle change"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    event_type: str
    employee_id: str
    employee_email: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    changes: List[ChangeDetail] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)
    source: str = "hris"  # Where the event originated
    correlation_id: Optional[str] = None  # For tracing


# =============================================================================
# ACCESS PROFILE MODELS (for RBAC)
# =============================================================================

class AccessProfile(BaseModel):
    """Access profile for role-based provisioning"""
    id: str
    name: str
    description: Optional[str] = None
    department_id: Optional[str] = None
    job_family: Optional[str] = None
    job_level: Optional[str] = None
    groups: List[str] = Field(default_factory=list)
    applications: List[str] = Field(default_factory=list)
    entitlements: Dict[str, List[str]] = Field(default_factory=dict)


class AccessRequest(BaseModel):
    """Access request for provisioning"""
    employee_id: str
    profile_id: str
    requested_by: str
    justification: Optional[str] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    status: str = "pending"
