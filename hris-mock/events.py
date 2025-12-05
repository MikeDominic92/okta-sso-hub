"""
HRIS Event Generator - Simulates real-world HR events for testing JML workflows

This module generates realistic HR events that trigger identity lifecycle
workflows in Okta:
- New hires (Joiner)
- Department transfers (Mover)
- Promotions/demotions (Mover)
- Manager changes (Mover)
- Terminations (Leaver)

Chainguard Relevance: Demonstrates event-driven identity lifecycle automation
required for IT Engineer (Identity/IAM) role.
"""

import asyncio
import random
import httpx
from datetime import datetime, date, timedelta
from typing import List, Optional, Dict, Any
from enum import Enum
from dataclasses import dataclass, field
from faker import Faker
import json
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

fake = Faker()


# =============================================================================
# CONFIGURATION
# =============================================================================

@dataclass
class EventGeneratorConfig:
    """Configuration for the event generator"""
    hris_base_url: str = "http://localhost:8000"
    okta_webhook_url: Optional[str] = None
    event_interval_seconds: float = 5.0
    batch_size: int = 1
    departments: List[str] = field(default_factory=lambda: [
        "Engineering", "Product", "Sales", "Marketing",
        "Finance", "HR", "IT", "Legal", "Operations"
    ])
    locations: List[str] = field(default_factory=lambda: [
        "San Francisco", "New York", "Seattle", "Austin",
        "Chicago", "Boston", "Denver", "Remote"
    ])
    titles_by_department: Dict[str, List[str]] = field(default_factory=lambda: {
        "Engineering": [
            "Software Engineer", "Senior Software Engineer",
            "Staff Engineer", "Principal Engineer", "Engineering Manager"
        ],
        "Product": [
            "Product Manager", "Senior Product Manager",
            "Director of Product", "VP Product"
        ],
        "Sales": [
            "Account Executive", "Senior AE",
            "Sales Manager", "Director of Sales"
        ],
        "Marketing": [
            "Marketing Specialist", "Marketing Manager",
            "Director of Marketing", "CMO"
        ],
        "Finance": [
            "Financial Analyst", "Senior Analyst",
            "Finance Manager", "Controller", "CFO"
        ],
        "HR": [
            "HR Coordinator", "HR Business Partner",
            "HR Manager", "Director of HR", "CHRO"
        ],
        "IT": [
            "IT Support", "Systems Administrator",
            "IT Manager", "Director of IT", "CIO"
        ],
        "Legal": [
            "Paralegal", "Associate Counsel",
            "Senior Counsel", "General Counsel"
        ],
        "Operations": [
            "Operations Analyst", "Operations Manager",
            "Director of Operations", "COO"
        ]
    })


class EventType(str, Enum):
    """Types of HR events"""
    NEW_HIRE = "new_hire"
    DEPARTMENT_TRANSFER = "department_transfer"
    PROMOTION = "promotion"
    MANAGER_CHANGE = "manager_change"
    LOCATION_CHANGE = "location_change"
    TERMINATION = "termination"
    LEAVE_OF_ABSENCE = "leave_of_absence"
    RETURN_FROM_LEAVE = "return_from_leave"


# =============================================================================
# EVENT GENERATORS
# =============================================================================

class HREventGenerator:
    """Generates realistic HR events for testing"""

    def __init__(self, config: EventGeneratorConfig = None):
        self.config = config or EventGeneratorConfig()
        self.employee_counter = 0
        self.generated_employees: List[Dict] = []

    def generate_employee_number(self) -> str:
        """Generate unique employee number"""
        self.employee_counter += 1
        return f"EMP{self.employee_counter:05d}"

    def generate_new_hire(self) -> Dict[str, Any]:
        """
        Generate a new hire event (JOINER)

        Returns employee data that will trigger new_hire_onboarding workflow
        """
        department = random.choice(self.config.departments)
        titles = self.config.titles_by_department.get(department, ["Analyst"])
        title = random.choice(titles[:3])  # New hires are usually junior

        start_date = date.today() + timedelta(days=random.randint(1, 30))

        employee = {
            "employee_number": self.generate_employee_number(),
            "email": fake.company_email(),
            "first_name": fake.first_name(),
            "last_name": fake.last_name(),
            "department": department,
            "department_id": department[:3].upper(),
            "title": title,
            "start_date": start_date.isoformat(),
            "location": random.choice(self.config.locations),
            "cost_center": f"CC-{department[:3].upper()}-{random.randint(100, 999)}",
            "employment_type": random.choice(["full_time", "contractor"]),
        }

        self.generated_employees.append(employee)
        return {
            "event_type": EventType.NEW_HIRE,
            "data": employee,
            "metadata": {
                "source": "hris_event_generator",
                "timestamp": datetime.utcnow().isoformat()
            }
        }

    def generate_department_transfer(self) -> Optional[Dict[str, Any]]:
        """
        Generate a department transfer event (MOVER)

        Returns event data that will trigger department_transfer workflow
        """
        if not self.generated_employees:
            return None

        employee = random.choice(self.generated_employees)
        old_department = employee.get("department")

        # Pick a different department
        new_department = random.choice([
            d for d in self.config.departments if d != old_department
        ])

        new_titles = self.config.titles_by_department.get(new_department, ["Analyst"])
        new_title = random.choice(new_titles[:3])

        return {
            "event_type": EventType.DEPARTMENT_TRANSFER,
            "employee_id": employee.get("employee_number"),
            "data": {
                "department": new_department,
                "department_id": new_department[:3].upper(),
                "title": new_title,
                "cost_center": f"CC-{new_department[:3].upper()}-{random.randint(100, 999)}"
            },
            "previous_values": {
                "department": old_department,
                "department_id": old_department[:3].upper() if old_department else None,
                "title": employee.get("title")
            },
            "metadata": {
                "source": "hris_event_generator",
                "timestamp": datetime.utcnow().isoformat(),
                "effective_date": (date.today() + timedelta(days=random.randint(1, 14))).isoformat()
            }
        }

    def generate_promotion(self) -> Optional[Dict[str, Any]]:
        """
        Generate a promotion event (MOVER)

        Returns event data for title change within same department
        """
        if not self.generated_employees:
            return None

        employee = random.choice(self.generated_employees)
        department = employee.get("department")
        current_title = employee.get("title")

        titles = self.config.titles_by_department.get(department, ["Analyst"])
        current_index = titles.index(current_title) if current_title in titles else 0

        # Promote to next level if possible
        if current_index < len(titles) - 1:
            new_title = titles[current_index + 1]
        else:
            return None  # Already at top

        return {
            "event_type": EventType.PROMOTION,
            "employee_id": employee.get("employee_number"),
            "data": {
                "title": new_title
            },
            "previous_values": {
                "title": current_title
            },
            "metadata": {
                "source": "hris_event_generator",
                "timestamp": datetime.utcnow().isoformat(),
                "effective_date": date.today().isoformat()
            }
        }

    def generate_manager_change(self) -> Optional[Dict[str, Any]]:
        """
        Generate a manager change event (MOVER)

        Returns event data that updates reporting structure
        """
        if len(self.generated_employees) < 2:
            return None

        employee = random.choice(self.generated_employees)
        potential_managers = [
            e for e in self.generated_employees
            if e.get("employee_number") != employee.get("employee_number")
            and e.get("department") == employee.get("department")
        ]

        if not potential_managers:
            return None

        new_manager = random.choice(potential_managers)

        return {
            "event_type": EventType.MANAGER_CHANGE,
            "employee_id": employee.get("employee_number"),
            "data": {
                "manager_id": new_manager.get("employee_number"),
                "manager_email": new_manager.get("email")
            },
            "previous_values": {
                "manager_id": employee.get("manager_id"),
                "manager_email": employee.get("manager_email")
            },
            "metadata": {
                "source": "hris_event_generator",
                "timestamp": datetime.utcnow().isoformat()
            }
        }

    def generate_termination(self) -> Optional[Dict[str, Any]]:
        """
        Generate a termination event (LEAVER)

        Returns event data that will trigger offboarding workflow
        """
        if not self.generated_employees:
            return None

        employee = random.choice(self.generated_employees)

        termination_types = [
            ("voluntary", 0.6),
            ("involuntary", 0.2),
            ("contract_end", 0.15),
            ("security_concern", 0.05)
        ]

        # Weighted random selection
        termination_type = random.choices(
            [t[0] for t in termination_types],
            weights=[t[1] for t in termination_types]
        )[0]

        # Compliance hold required for involuntary or security
        compliance_hold = termination_type in ["involuntary", "security_concern"]

        termination_date = date.today() + timedelta(days=random.randint(1, 14))
        if termination_type == "security_concern":
            termination_date = date.today()  # Immediate

        return {
            "event_type": EventType.TERMINATION,
            "employee_id": employee.get("employee_number"),
            "data": {
                "termination_date": termination_date.isoformat(),
                "termination_type": termination_type,
                "compliance_hold": compliance_hold,
                "last_day_worked": (termination_date - timedelta(days=1)).isoformat()
            },
            "previous_values": {
                "employment_status": "active"
            },
            "metadata": {
                "source": "hris_event_generator",
                "timestamp": datetime.utcnow().isoformat()
            }
        }

    def generate_random_event(self) -> Dict[str, Any]:
        """
        Generate a random HR event

        Weighted distribution:
        - New hires: 40%
        - Department transfers: 15%
        - Promotions: 15%
        - Manager changes: 10%
        - Terminations: 20%
        """
        event_weights = [
            (EventType.NEW_HIRE, 0.40),
            (EventType.DEPARTMENT_TRANSFER, 0.15),
            (EventType.PROMOTION, 0.15),
            (EventType.MANAGER_CHANGE, 0.10),
            (EventType.TERMINATION, 0.20),
        ]

        event_type = random.choices(
            [e[0] for e in event_weights],
            weights=[e[1] for e in event_weights]
        )[0]

        generators = {
            EventType.NEW_HIRE: self.generate_new_hire,
            EventType.DEPARTMENT_TRANSFER: self.generate_department_transfer,
            EventType.PROMOTION: self.generate_promotion,
            EventType.MANAGER_CHANGE: self.generate_manager_change,
            EventType.TERMINATION: self.generate_termination,
        }

        event = generators[event_type]()

        # If event generation failed (no employees yet), generate new hire
        if event is None:
            event = self.generate_new_hire()

        return event


# =============================================================================
# EVENT SENDER
# =============================================================================

class EventSender:
    """Sends generated events to HRIS API and webhooks"""

    def __init__(self, config: EventGeneratorConfig):
        self.config = config

    async def send_to_hris(self, event: Dict[str, Any]) -> Dict[str, Any]:
        """Send event to HRIS mock server"""
        event_type = event.get("event_type")

        async with httpx.AsyncClient() as client:
            if event_type == EventType.NEW_HIRE:
                response = await client.post(
                    f"{self.config.hris_base_url}/api/v1/employees",
                    json=event["data"]
                )
            elif event_type == EventType.TERMINATION:
                employee_id = event.get("employee_id")
                response = await client.post(
                    f"{self.config.hris_base_url}/api/v1/employees/{employee_id}/terminate",
                    json=event["data"]
                )
            else:
                # Updates (transfer, promotion, manager change)
                employee_id = event.get("employee_id")
                response = await client.patch(
                    f"{self.config.hris_base_url}/api/v1/employees/{employee_id}",
                    json=event["data"]
                )

            return {
                "status_code": response.status_code,
                "response": response.json() if response.status_code < 400 else None,
                "error": response.text if response.status_code >= 400 else None
            }


# =============================================================================
# EVENT STREAM
# =============================================================================

async def run_event_stream(
    config: EventGeneratorConfig = None,
    num_events: int = None,
    continuous: bool = False
):
    """
    Run continuous event generation for testing

    Args:
        config: Event generator configuration
        num_events: Number of events to generate (None for continuous)
        continuous: Run continuously until interrupted
    """
    config = config or EventGeneratorConfig()
    generator = HREventGenerator(config)
    sender = EventSender(config)

    events_generated = 0

    logger.info("Starting HR event generator...")
    logger.info(f"HRIS URL: {config.hris_base_url}")

    try:
        while continuous or (num_events is None) or (events_generated < num_events):
            event = generator.generate_random_event()

            logger.info(f"Generated event: {event['event_type'].value}")
            logger.info(f"Event data: {json.dumps(event, default=str, indent=2)}")

            try:
                result = await sender.send_to_hris(event)
                logger.info(f"HRIS response: {result['status_code']}")
            except Exception as e:
                logger.error(f"Failed to send event: {e}")

            events_generated += 1

            if not (num_events and events_generated >= num_events):
                await asyncio.sleep(config.event_interval_seconds)

    except KeyboardInterrupt:
        logger.info("Event generator stopped by user")

    logger.info(f"Total events generated: {events_generated}")


# =============================================================================
# CLI INTERFACE
# =============================================================================

def main():
    """CLI entry point"""
    import argparse

    parser = argparse.ArgumentParser(description="HRIS Event Generator")
    parser.add_argument(
        "--url",
        default="http://localhost:8000",
        help="HRIS server URL"
    )
    parser.add_argument(
        "--count",
        type=int,
        default=10,
        help="Number of events to generate"
    )
    parser.add_argument(
        "--interval",
        type=float,
        default=2.0,
        help="Seconds between events"
    )
    parser.add_argument(
        "--continuous",
        action="store_true",
        help="Run continuously"
    )

    args = parser.parse_args()

    config = EventGeneratorConfig(
        hris_base_url=args.url,
        event_interval_seconds=args.interval
    )

    asyncio.run(run_event_stream(
        config=config,
        num_events=args.count if not args.continuous else None,
        continuous=args.continuous
    ))


if __name__ == "__main__":
    main()
