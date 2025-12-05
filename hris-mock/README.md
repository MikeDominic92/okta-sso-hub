# HRIS Mock Server

> **Chainguard Relevance:** This component demonstrates HRIS integration expertise required for IT Engineer (Identity/IAM) roles - specifically "identity lifecycle automation using Okta Workflows and HRIS integrations."

## Overview

A mock HRIS (Human Resources Information System) server that simulates enterprise HR platforms like Workday, BambooHR, and Rippling. This enables testing of identity lifecycle workflows without connecting to production HR systems.

## Features

### Core Capabilities

- **REST API** - Full CRUD operations for employee management
- **SCIM 2.0** - Standard protocol for identity provisioning
- **Webhooks** - Real-time event notifications to Okta
- **Event Generator** - Simulate realistic HR events for testing

### Supported JML Events

| Event Type | Trigger | Okta Workflow |
|------------|---------|---------------|
| New Hire | Employee created | `new_hire_onboarding_v2.json` |
| Department Transfer | Department changed | `department_transfer.json` |
| Promotion | Title changed | `department_transfer.json` |
| Manager Change | Manager updated | `department_transfer.json` |
| Termination | Employment ended | `offboarding_v2.json` |

## Quick Start

### 1. Install Dependencies

```bash
cd hris-mock
pip install -r requirements.txt
```

### 2. Start the Server

```bash
uvicorn server:app --reload --port 8000
```

### 3. Access the API

- **API Documentation:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc
- **Health Check:** http://localhost:8000/

## API Endpoints

### Employee Management

```bash
# List all employees
GET /api/v1/employees

# Get employee by ID
GET /api/v1/employees/{id}

# Create new employee (triggers JOINER event)
POST /api/v1/employees

# Update employee (triggers MOVER event)
PATCH /api/v1/employees/{id}

# Terminate employee (triggers LEAVER event)
POST /api/v1/employees/{id}/terminate
```

### SCIM 2.0

```bash
# List users (SCIM format)
GET /scim/v2/Users

# Get user (SCIM format)
GET /scim/v2/Users/{id}
```

### Webhooks

```bash
# Register webhook endpoint
POST /api/v1/webhooks

# List configured webhooks
GET /api/v1/webhooks

# View event log
GET /api/v1/events
```

## Example Requests

### Create New Employee (Joiner)

```bash
curl -X POST http://localhost:8000/api/v1/employees \
  -H "Content-Type: application/json" \
  -d '{
    "employee_number": "EMP001",
    "email": "john.doe@example.com",
    "first_name": "John",
    "last_name": "Doe",
    "department": "Engineering",
    "department_id": "ENG",
    "title": "Software Engineer",
    "start_date": "2025-01-15",
    "location": "San Francisco",
    "cost_center": "CC-ENG-001"
  }'
```

### Department Transfer (Mover)

```bash
curl -X PATCH http://localhost:8000/api/v1/employees/{id} \
  -H "Content-Type: application/json" \
  -d '{
    "department": "Product",
    "department_id": "PROD",
    "title": "Product Manager"
  }'
```

### Terminate Employee (Leaver)

```bash
curl -X POST http://localhost:8000/api/v1/employees/{id}/terminate \
  -H "Content-Type: application/json" \
  -d '{
    "termination_date": "2025-12-31",
    "termination_type": "voluntary",
    "compliance_hold": false
  }'
```

### Register Okta Webhook

```bash
curl -X POST http://localhost:8000/api/v1/webhooks \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://your-okta-domain.okta.com/api/v1/workflows/...",
    "events": ["employee.created", "employee.updated", "employee.terminated"],
    "secret": "your-webhook-secret",
    "active": true
  }'
```

## Event Generator

Generate realistic HR events for testing:

```bash
# Generate 10 random events
python events.py --count 10

# Run continuously with 5-second intervals
python events.py --continuous --interval 5

# Target specific HRIS server
python events.py --url http://localhost:8000 --count 20
```

### Event Distribution

| Event Type | Probability |
|------------|-------------|
| New Hire | 40% |
| Termination | 20% |
| Department Transfer | 15% |
| Promotion | 15% |
| Manager Change | 10% |

## Data Models

### Employee Schema

```python
{
    "id": "uuid",
    "employee_number": "EMP001",
    "email": "user@example.com",
    "first_name": "John",
    "last_name": "Doe",
    "display_name": "John Doe",
    "department": "Engineering",
    "department_id": "ENG",
    "title": "Software Engineer",
    "manager_id": "EMP000",
    "manager_email": "manager@example.com",
    "employment_status": "active|pending|terminated|on_leave",
    "employment_type": "full_time|part_time|contractor|intern",
    "start_date": "2025-01-15",
    "termination_date": null,
    "termination_type": null,
    "location": "San Francisco",
    "cost_center": "CC-ENG-001"
}
```

### Webhook Event Schema

```python
{
    "id": "event-uuid",
    "event_type": "employee.created|employee.updated|employee.terminated",
    "timestamp": "2025-12-05T10:30:00Z",
    "employee_id": "emp-uuid",
    "employee_email": "user@example.com",
    "data": { /* current employee data */ },
    "previous_values": { /* changed fields only */ }
}
```

## Integration with Okta

### Okta Workflows Integration

1. **Create Okta Workflow** with HTTP Receive trigger
2. **Register webhook** in HRIS mock server
3. **Map event types** to workflow actions:
   - `employee.created` → Run Joiner workflow
   - `employee.department_changed` → Run Mover workflow
   - `employee.terminated` → Run Leaver workflow

### Attribute Mapping

| HRIS Field | Okta Profile Attribute |
|------------|------------------------|
| email | login, email |
| first_name | firstName |
| last_name | lastName |
| department | department |
| title | title |
| manager_email | manager |
| employee_number | employeeNumber |
| cost_center | costCenter |
| start_date | startDate |

## Architecture

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│   HR Admin UI   │────▶│  HRIS Mock API  │────▶│  Okta Workflows │
└─────────────────┘     └─────────────────┘     └─────────────────┘
                               │
                               ▼
                        ┌─────────────────┐
                        │  Event Generator │
                        │  (Testing Tool)  │
                        └─────────────────┘
```

## Enterprise HRIS Compatibility

This mock server follows patterns from:

- **Workday** - SCIM 2.0, custom event webhooks
- **BambooHR** - REST API, webhook notifications
- **Rippling** - SCIM 2.0, real-time sync
- **ADP** - REST API integration patterns

## Testing Scenarios

1. **New Hire Day 1** - Create employee, verify provisioning
2. **Department Transfer** - Update department, verify access changes
3. **Promotion** - Update title, verify group membership changes
4. **Termination** - Initiate termination, verify access revocation
5. **Security Termination** - Immediate termination with compliance hold

## Author

**Mike Dominic** - December 2025

This component demonstrates enterprise HRIS integration patterns aligned with Chainguard IT Engineer (Identity/IAM) requirements for identity lifecycle automation.
