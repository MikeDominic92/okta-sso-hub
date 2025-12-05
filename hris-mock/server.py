"""
HRIS Mock Server - Simulates enterprise HRIS systems (Workday, BambooHR, Rippling)

This mock server demonstrates HRIS integration patterns for identity lifecycle management.
It provides:
- SCIM 2.0 endpoints for user provisioning
- Webhook events for JML (Joiner/Mover/Leaver) triggers
- REST API for employee data queries

Chainguard Relevance: Demonstrates HRIS integration expertise required for
IT Engineer (Identity/IAM) role - specifically "Okta Workflows and HRIS integrations"
"""

from fastapi import FastAPI, HTTPException, Header, BackgroundTasks, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
from datetime import datetime, date
from enum import Enum
import uuid
import asyncio
import httpx
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="HRIS Mock Server",
    description="Simulates enterprise HRIS systems for IAM integration testing",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# =============================================================================
# ENUMS AND MODELS
# =============================================================================

class EmploymentStatus(str, Enum):
    ACTIVE = "active"
    PENDING = "pending"
    TERMINATED = "terminated"
    ON_LEAVE = "on_leave"


class EmploymentType(str, Enum):
    FULL_TIME = "full_time"
    PART_TIME = "part_time"
    CONTRACTOR = "contractor"
    INTERN = "intern"


class TerminationType(str, Enum):
    VOLUNTARY = "voluntary"
    INVOLUNTARY = "involuntary"
    RETIREMENT = "retirement"
    CONTRACT_END = "contract_end"
    SECURITY_CONCERN = "security_concern"


class EventType(str, Enum):
    EMPLOYEE_CREATED = "employee.created"
    EMPLOYEE_UPDATED = "employee.updated"
    EMPLOYEE_TERMINATED = "employee.terminated"
    DEPARTMENT_CHANGED = "employee.department_changed"
    MANAGER_CHANGED = "employee.manager_changed"
    TITLE_CHANGED = "employee.title_changed"


class Employee(BaseModel):
    """Employee data model matching HRIS schema"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    employee_number: str
    email: EmailStr
    first_name: str
    last_name: str
    display_name: Optional[str] = None
    department: str
    department_id: str
    title: str
    manager_id: Optional[str] = None
    manager_email: Optional[EmailStr] = None
    employment_status: EmploymentStatus = EmploymentStatus.PENDING
    employment_type: EmploymentType = EmploymentType.FULL_TIME
    start_date: date
    termination_date: Optional[date] = None
    termination_type: Optional[TerminationType] = None
    location: str
    cost_center: str
    work_phone: Optional[str] = None
    mobile_phone: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat(),
            date: lambda v: v.isoformat()
        }


class EmployeeCreate(BaseModel):
    """Request model for creating an employee"""
    employee_number: str
    email: EmailStr
    first_name: str
    last_name: str
    department: str
    department_id: str
    title: str
    manager_id: Optional[str] = None
    manager_email: Optional[EmailStr] = None
    employment_type: EmploymentType = EmploymentType.FULL_TIME
    start_date: date
    location: str
    cost_center: str


class EmployeeUpdate(BaseModel):
    """Request model for updating an employee"""
    department: Optional[str] = None
    department_id: Optional[str] = None
    title: Optional[str] = None
    manager_id: Optional[str] = None
    manager_email: Optional[EmailStr] = None
    location: Optional[str] = None
    cost_center: Optional[str] = None
    employment_status: Optional[EmploymentStatus] = None


class TerminationRequest(BaseModel):
    """Request model for terminating an employee"""
    termination_date: date
    termination_type: TerminationType
    compliance_hold: bool = False
    last_day_worked: Optional[date] = None
    reason: Optional[str] = None


class WebhookEvent(BaseModel):
    """Webhook event payload sent to Okta"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    event_type: EventType
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    employee_id: str
    employee_email: str
    data: dict
    previous_values: Optional[dict] = None


class WebhookConfig(BaseModel):
    """Webhook configuration"""
    url: str
    events: List[EventType]
    secret: Optional[str] = None
    active: bool = True


# =============================================================================
# IN-MEMORY DATABASE (for demo purposes)
# =============================================================================

employees_db: dict[str, Employee] = {}
webhook_configs: List[WebhookConfig] = []
event_log: List[WebhookEvent] = []

# Sample departments
DEPARTMENTS = {
    "ENG": {"name": "Engineering", "id": "ENG"},
    "SALES": {"name": "Sales", "id": "SALES"},
    "FIN": {"name": "Finance", "id": "FIN"},
    "HR": {"name": "Human Resources", "id": "HR"},
    "IT": {"name": "Information Technology", "id": "IT"},
    "PROD": {"name": "Product", "id": "PROD"},
    "MKT": {"name": "Marketing", "id": "MKT"},
}


# =============================================================================
# WEBHOOK DELIVERY
# =============================================================================

async def send_webhook(event: WebhookEvent):
    """Send webhook event to configured endpoints"""
    for config in webhook_configs:
        if not config.active:
            continue
        if event.event_type not in config.events:
            continue

        try:
            async with httpx.AsyncClient() as client:
                headers = {
                    "Content-Type": "application/json",
                    "X-HRIS-Event": event.event_type.value,
                    "X-HRIS-Signature": config.secret or "none"
                }
                response = await client.post(
                    config.url,
                    json=event.dict(),
                    headers=headers,
                    timeout=30.0
                )
                logger.info(f"Webhook sent to {config.url}: {response.status_code}")
        except Exception as e:
            logger.error(f"Webhook delivery failed: {e}")


def trigger_event(
    event_type: EventType,
    employee: Employee,
    previous_values: dict = None
):
    """Create and queue a webhook event"""
    event = WebhookEvent(
        event_type=event_type,
        employee_id=employee.id,
        employee_email=employee.email,
        data=employee.dict(),
        previous_values=previous_values
    )
    event_log.append(event)

    # Fire and forget webhook delivery
    asyncio.create_task(send_webhook(event))

    return event


# =============================================================================
# API ENDPOINTS - Employee Management
# =============================================================================

@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "service": "HRIS Mock Server",
        "version": "1.0.0",
        "status": "healthy",
        "employees_count": len(employees_db),
        "chainguard_relevance": "Demonstrates HRIS integration for IT Engineer (Identity/IAM) role"
    }


@app.get("/api/v1/employees", response_model=List[Employee])
async def list_employees(
    status: Optional[EmploymentStatus] = None,
    department: Optional[str] = None,
    limit: int = 100,
    offset: int = 0
):
    """List all employees with optional filtering"""
    employees = list(employees_db.values())

    if status:
        employees = [e for e in employees if e.employment_status == status]
    if department:
        employees = [e for e in employees if e.department == department]

    return employees[offset:offset + limit]


@app.get("/api/v1/employees/{employee_id}", response_model=Employee)
async def get_employee(employee_id: str):
    """Get a specific employee by ID"""
    if employee_id not in employees_db:
        raise HTTPException(status_code=404, detail="Employee not found")
    return employees_db[employee_id]


@app.post("/api/v1/employees", response_model=Employee, status_code=201)
async def create_employee(employee_data: EmployeeCreate, background_tasks: BackgroundTasks):
    """
    Create a new employee (JOINER event)

    This triggers the new_hire_onboarding workflow in Okta.
    """
    employee = Employee(
        **employee_data.dict(),
        display_name=f"{employee_data.first_name} {employee_data.last_name}",
        employment_status=EmploymentStatus.PENDING
    )

    employees_db[employee.id] = employee

    # Trigger JOINER event
    event = trigger_event(EventType.EMPLOYEE_CREATED, employee)

    logger.info(f"Employee created: {employee.email} - Event: {event.id}")

    return employee


@app.patch("/api/v1/employees/{employee_id}", response_model=Employee)
async def update_employee(
    employee_id: str,
    updates: EmployeeUpdate,
    background_tasks: BackgroundTasks
):
    """
    Update an employee (potential MOVER event)

    This triggers the department_transfer workflow if department/title/manager changes.
    """
    if employee_id not in employees_db:
        raise HTTPException(status_code=404, detail="Employee not found")

    employee = employees_db[employee_id]
    previous_values = {}
    events_to_trigger = []

    update_data = updates.dict(exclude_unset=True)

    for field, value in update_data.items():
        if hasattr(employee, field):
            old_value = getattr(employee, field)
            if old_value != value:
                previous_values[field] = old_value
                setattr(employee, field, value)

                # Determine which event to trigger
                if field == "department":
                    events_to_trigger.append(EventType.DEPARTMENT_CHANGED)
                elif field == "title":
                    events_to_trigger.append(EventType.TITLE_CHANGED)
                elif field == "manager_id":
                    events_to_trigger.append(EventType.MANAGER_CHANGED)

    employee.updated_at = datetime.utcnow()
    employees_db[employee_id] = employee

    # Trigger appropriate MOVER events
    if events_to_trigger:
        for event_type in events_to_trigger:
            trigger_event(event_type, employee, previous_values)

        # Also trigger general update event
        trigger_event(EventType.EMPLOYEE_UPDATED, employee, previous_values)

    logger.info(f"Employee updated: {employee.email} - Changes: {list(previous_values.keys())}")

    return employee


@app.post("/api/v1/employees/{employee_id}/terminate", response_model=Employee)
async def terminate_employee(
    employee_id: str,
    termination: TerminationRequest,
    background_tasks: BackgroundTasks
):
    """
    Terminate an employee (LEAVER event)

    This triggers the offboarding workflow in Okta.
    """
    if employee_id not in employees_db:
        raise HTTPException(status_code=404, detail="Employee not found")

    employee = employees_db[employee_id]
    previous_status = employee.employment_status

    employee.employment_status = EmploymentStatus.TERMINATED
    employee.termination_date = termination.termination_date
    employee.termination_type = termination.termination_type
    employee.updated_at = datetime.utcnow()

    employees_db[employee_id] = employee

    # Trigger LEAVER event with compliance hold flag
    event = trigger_event(
        EventType.EMPLOYEE_TERMINATED,
        employee,
        previous_values={
            "employment_status": previous_status.value,
            "compliance_hold": termination.compliance_hold,
            "termination_reason": termination.reason
        }
    )

    logger.info(f"Employee terminated: {employee.email} - Type: {termination.termination_type}")

    return employee


# =============================================================================
# API ENDPOINTS - Webhook Management
# =============================================================================

@app.get("/api/v1/webhooks", response_model=List[WebhookConfig])
async def list_webhooks():
    """List all configured webhooks"""
    return webhook_configs


@app.post("/api/v1/webhooks", response_model=WebhookConfig, status_code=201)
async def create_webhook(config: WebhookConfig):
    """Register a new webhook endpoint"""
    webhook_configs.append(config)
    logger.info(f"Webhook registered: {config.url} for events: {config.events}")
    return config


@app.delete("/api/v1/webhooks/{webhook_url}")
async def delete_webhook(webhook_url: str):
    """Remove a webhook configuration"""
    global webhook_configs
    webhook_configs = [w for w in webhook_configs if w.url != webhook_url]
    return {"status": "deleted"}


# =============================================================================
# API ENDPOINTS - Event Log
# =============================================================================

@app.get("/api/v1/events", response_model=List[WebhookEvent])
async def list_events(
    event_type: Optional[EventType] = None,
    employee_id: Optional[str] = None,
    limit: int = 50
):
    """Get recent events from the event log"""
    events = event_log.copy()

    if event_type:
        events = [e for e in events if e.event_type == event_type]
    if employee_id:
        events = [e for e in events if e.employee_id == employee_id]

    return events[-limit:]


# =============================================================================
# API ENDPOINTS - Department Reference Data
# =============================================================================

@app.get("/api/v1/departments")
async def list_departments():
    """Get all department reference data"""
    return DEPARTMENTS


# =============================================================================
# SCIM 2.0 ENDPOINTS (for Okta integration)
# =============================================================================

@app.get("/scim/v2/Users")
async def scim_list_users(
    filter: Optional[str] = None,
    startIndex: int = 1,
    count: int = 100
):
    """SCIM 2.0 - List Users"""
    users = list(employees_db.values())

    scim_users = []
    for emp in users:
        scim_users.append({
            "schemas": ["urn:ietf:params:scim:schemas:core:2.0:User"],
            "id": emp.id,
            "externalId": emp.employee_number,
            "userName": emp.email,
            "name": {
                "givenName": emp.first_name,
                "familyName": emp.last_name,
                "formatted": emp.display_name
            },
            "emails": [{"value": emp.email, "primary": True}],
            "active": emp.employment_status == EmploymentStatus.ACTIVE,
            "title": emp.title,
            "urn:ietf:params:scim:schemas:extension:enterprise:2.0:User": {
                "employeeNumber": emp.employee_number,
                "department": emp.department,
                "manager": {"value": emp.manager_id}
            }
        })

    return {
        "schemas": ["urn:ietf:params:scim:api:messages:2.0:ListResponse"],
        "totalResults": len(scim_users),
        "startIndex": startIndex,
        "itemsPerPage": count,
        "Resources": scim_users[startIndex-1:startIndex-1+count]
    }


@app.get("/scim/v2/Users/{user_id}")
async def scim_get_user(user_id: str):
    """SCIM 2.0 - Get User"""
    if user_id not in employees_db:
        raise HTTPException(status_code=404, detail="User not found")

    emp = employees_db[user_id]
    return {
        "schemas": ["urn:ietf:params:scim:schemas:core:2.0:User"],
        "id": emp.id,
        "externalId": emp.employee_number,
        "userName": emp.email,
        "name": {
            "givenName": emp.first_name,
            "familyName": emp.last_name,
            "formatted": emp.display_name
        },
        "emails": [{"value": emp.email, "primary": True}],
        "active": emp.employment_status == EmploymentStatus.ACTIVE,
        "title": emp.title,
        "urn:ietf:params:scim:schemas:extension:enterprise:2.0:User": {
            "employeeNumber": emp.employee_number,
            "department": emp.department,
            "manager": {"value": emp.manager_id}
        }
    }


# =============================================================================
# DEMO DATA LOADER
# =============================================================================

@app.post("/api/v1/demo/load")
async def load_demo_data():
    """Load sample employee data for demo purposes"""
    demo_employees = [
        EmployeeCreate(
            employee_number="EMP001",
            email="john.smith@example.com",
            first_name="John",
            last_name="Smith",
            department="Engineering",
            department_id="ENG",
            title="Senior Software Engineer",
            start_date=date(2023, 1, 15),
            location="San Francisco",
            cost_center="CC-ENG-001"
        ),
        EmployeeCreate(
            employee_number="EMP002",
            email="jane.doe@example.com",
            first_name="Jane",
            last_name="Doe",
            department="Product",
            department_id="PROD",
            title="Product Manager",
            manager_id="EMP001",
            start_date=date(2023, 3, 1),
            location="New York",
            cost_center="CC-PROD-001"
        ),
        EmployeeCreate(
            employee_number="EMP003",
            email="bob.wilson@example.com",
            first_name="Bob",
            last_name="Wilson",
            department="Sales",
            department_id="SALES",
            title="Account Executive",
            start_date=date(2023, 6, 15),
            location="Chicago",
            cost_center="CC-SALES-001"
        ),
    ]

    created = []
    for emp_data in demo_employees:
        emp = Employee(
            **emp_data.dict(),
            display_name=f"{emp_data.first_name} {emp_data.last_name}",
            employment_status=EmploymentStatus.ACTIVE
        )
        employees_db[emp.id] = emp
        created.append(emp.email)

    return {"status": "success", "employees_created": created}


# =============================================================================
# MAIN
# =============================================================================

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
