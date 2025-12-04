"""
SSO Event-Driven Workflow Trigger

v1.1 Enhancement - December 2025
Triggers Okta Workflows based on SSO authentication and lifecycle events.

Features:
- Monitor SSO authentication events
- Trigger workflows based on event types
- Correlate workflow executions with SSO events
- Event filtering and routing
- Configurable trigger rules
- Mock event simulation for demos
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any, Callable
from datetime import datetime
from enum import Enum
from dataclasses import dataclass, field
import json

from .flow_executor import FlowExecutor, ExecutionResult


# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SSOEventType(Enum):
    """SSO event type enumeration"""
    # Authentication events
    LOGIN_SUCCESS = "user.authentication.sso.login.success"
    LOGIN_FAILURE = "user.authentication.sso.login.failure"
    LOGOUT = "user.authentication.sso.logout"
    SESSION_EXPIRED = "user.session.expired"

    # MFA events
    MFA_ENROLLED = "user.mfa.factor.activate"
    MFA_CHALLENGE = "user.mfa.factor.challenge"
    MFA_FAILURE = "user.mfa.factor.failure"

    # User lifecycle events
    USER_CREATED = "user.lifecycle.create"
    USER_ACTIVATED = "user.lifecycle.activate"
    USER_DEACTIVATED = "user.lifecycle.deactivate"
    USER_SUSPENDED = "user.lifecycle.suspend"
    USER_UNSUSPENDED = "user.lifecycle.unsuspend"

    # Access events
    APP_ACCESS_GRANTED = "application.user_membership.add"
    APP_ACCESS_REVOKED = "application.user_membership.remove"
    GROUP_MEMBERSHIP_ADD = "group.user_membership.add"
    GROUP_MEMBERSHIP_REMOVE = "group.user_membership.remove"

    # Password events
    PASSWORD_CHANGED = "user.account.update_password"
    PASSWORD_RESET = "user.account.reset_password"
    PASSWORD_EXPIRING = "user.password.expiring"

    # Policy events
    POLICY_VIOLATION = "policy.violation"
    RISKY_LOGIN = "user.authentication.risk.detected"


@dataclass
class SSOEvent:
    """
    SSO event data container.

    Attributes:
        event_id: Unique event identifier
        event_type: Type of SSO event
        timestamp: Event timestamp
        user_id: Okta user ID
        user_email: User email address
        client_ip: Client IP address
        user_agent: User agent string
        metadata: Additional event metadata
    """
    event_id: str
    event_type: str
    timestamp: str
    user_id: Optional[str] = None
    user_email: Optional[str] = None
    client_ip: Optional[str] = None
    user_agent: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert event to dictionary"""
        return {
            'event_id': self.event_id,
            'event_type': self.event_type,
            'timestamp': self.timestamp,
            'user_id': self.user_id,
            'user_email': self.user_email,
            'client_ip': self.client_ip,
            'user_agent': self.user_agent,
            'metadata': self.metadata
        }


@dataclass
class TriggerRule:
    """
    Workflow trigger rule configuration.

    Attributes:
        rule_id: Unique rule identifier
        event_types: List of event types that trigger this rule
        flow_id: Workflow flow to execute
        condition: Optional condition function to evaluate
        input_transformer: Function to transform event data to flow input
        enabled: Whether rule is active
    """
    rule_id: str
    event_types: List[str]
    flow_id: str
    condition: Optional[Callable[[SSOEvent], bool]] = None
    input_transformer: Optional[Callable[[SSOEvent], Dict[str, Any]]] = None
    enabled: bool = True


class EventTrigger:
    """
    Event-driven workflow trigger system.

    This class monitors SSO events and triggers appropriate workflows based on
    configured rules. It provides:
    - Event ingestion and routing
    - Rule-based workflow triggering
    - Event-workflow correlation
    - Configurable trigger conditions
    - Event history tracking

    Attributes:
        executor: FlowExecutor instance for workflow execution
        rules: List of configured trigger rules
        event_history: History of processed events
    """

    def __init__(
        self,
        executor: Optional[FlowExecutor] = None,
        mock_mode: bool = False
    ):
        """
        Initialize EventTrigger.

        Args:
            executor: FlowExecutor instance (created if not provided)
            mock_mode: Enable mock mode for demonstrations
        """
        self.executor = executor or FlowExecutor(mock_mode=mock_mode)
        self.mock_mode = mock_mode

        # Trigger rules
        self._rules: List[TriggerRule] = []

        # Event history
        self._event_history: List[SSOEvent] = []

        # Event-workflow correlation
        self._event_workflow_map: Dict[str, List[str]] = {}

        # Initialize default rules
        self._initialize_default_rules()

        logger.info(f"EventTrigger initialized (mock_mode={mock_mode})")

    def _initialize_default_rules(self):
        """Initialize default trigger rules"""

        # Rule 1: New user onboarding
        self.add_rule(TriggerRule(
            rule_id='rule_new_hire_onboarding',
            event_types=[SSOEventType.USER_CREATED.value, SSOEventType.USER_ACTIVATED.value],
            flow_id='flow_new_hire_onboarding',
            input_transformer=lambda event: {
                'user_id': event.user_id,
                'user_email': event.user_email,
                'event_timestamp': event.timestamp
            }
        ))

        # Rule 2: User offboarding
        self.add_rule(TriggerRule(
            rule_id='rule_offboarding',
            event_types=[SSOEventType.USER_DEACTIVATED.value],
            flow_id='flow_offboarding',
            input_transformer=lambda event: {
                'user_id': event.user_id,
                'user_email': event.user_email,
                'deactivation_time': event.timestamp
            }
        ))

        # Rule 3: MFA remediation on login failure
        self.add_rule(TriggerRule(
            rule_id='rule_mfa_remediation',
            event_types=[SSOEventType.LOGIN_FAILURE.value],
            flow_id='flow_mfa_remediation',
            condition=lambda event: event.metadata.get('reason') == 'mfa_not_enrolled',
            input_transformer=lambda event: {
                'user_id': event.user_id,
                'user_email': event.user_email,
                'failure_reason': event.metadata.get('reason')
            }
        ))

        # Rule 4: Password expiry notification
        self.add_rule(TriggerRule(
            rule_id='rule_password_expiry',
            event_types=[SSOEventType.PASSWORD_EXPIRING.value],
            flow_id='flow_password_expiry',
            input_transformer=lambda event: {
                'user_id': event.user_id,
                'user_email': event.user_email,
                'expiry_date': event.metadata.get('expiry_date')
            }
        ))

        # Rule 5: Application access request
        self.add_rule(TriggerRule(
            rule_id='rule_access_request',
            event_types=[SSOEventType.APP_ACCESS_GRANTED.value],
            flow_id='flow_access_request',
            input_transformer=lambda event: {
                'user_id': event.user_id,
                'user_email': event.user_email,
                'app_id': event.metadata.get('app_id'),
                'app_name': event.metadata.get('app_name')
            }
        ))

        logger.info(f"Initialized {len(self._rules)} default trigger rules")

    def add_rule(self, rule: TriggerRule):
        """
        Add a trigger rule.

        Args:
            rule: TriggerRule to add
        """
        self._rules.append(rule)
        logger.info(f"Added trigger rule: {rule.rule_id} for flow {rule.flow_id}")

    def remove_rule(self, rule_id: str) -> bool:
        """
        Remove a trigger rule by ID.

        Args:
            rule_id: Rule identifier

        Returns:
            True if rule was removed, False if not found
        """
        original_count = len(self._rules)
        self._rules = [r for r in self._rules if r.rule_id != rule_id]
        removed = len(self._rules) < original_count

        if removed:
            logger.info(f"Removed trigger rule: {rule_id}")

        return removed

    def get_rule(self, rule_id: str) -> Optional[TriggerRule]:
        """
        Get a trigger rule by ID.

        Args:
            rule_id: Rule identifier

        Returns:
            TriggerRule if found, None otherwise
        """
        for rule in self._rules:
            if rule.rule_id == rule_id:
                return rule
        return None

    def list_rules(self, enabled_only: bool = False) -> List[TriggerRule]:
        """
        List all trigger rules.

        Args:
            enabled_only: Only return enabled rules

        Returns:
            List of TriggerRule objects
        """
        if enabled_only:
            return [r for r in self._rules if r.enabled]
        return self._rules.copy()

    async def process_event(self, event: SSOEvent) -> List[ExecutionResult]:
        """
        Process an SSO event and trigger applicable workflows.

        Args:
            event: SSOEvent to process

        Returns:
            List of ExecutionResult objects for triggered workflows
        """
        logger.info(f"Processing event: {event.event_type} (user: {event.user_email})")

        # Add to history
        self._event_history.append(event)

        # Find matching rules
        matching_rules = self._find_matching_rules(event)

        if not matching_rules:
            logger.info(f"No matching rules for event {event.event_type}")
            return []

        logger.info(f"Found {len(matching_rules)} matching rules")

        # Execute workflows for matching rules
        results = []
        execution_ids = []

        for rule in matching_rules:
            try:
                # Transform event data to flow input
                input_data = self._transform_event_to_input(event, rule)

                # Execute workflow
                result = await self.executor.execute_flow(
                    flow_id=rule.flow_id,
                    input_data=input_data
                )

                results.append(result)
                execution_ids.append(result.execution_id)

                logger.info(
                    f"Triggered workflow {rule.flow_id} (execution: {result.execution_id}) "
                    f"for event {event.event_id}"
                )

            except Exception as e:
                logger.error(f"Failed to trigger workflow for rule {rule.rule_id}: {e}")

        # Store event-workflow correlation
        if execution_ids:
            self._event_workflow_map[event.event_id] = execution_ids

        return results

    async def process_events_batch(
        self,
        events: List[SSOEvent],
        parallel: bool = True
    ) -> Dict[str, List[ExecutionResult]]:
        """
        Process a batch of SSO events.

        Args:
            events: List of SSOEvent objects
            parallel: Process events in parallel

        Returns:
            Dictionary mapping event IDs to execution results
        """
        logger.info(f"Processing {len(events)} events ({'parallel' if parallel else 'sequential'})")

        results_map = {}

        if parallel:
            tasks = [self.process_event(event) for event in events]
            all_results = await asyncio.gather(*tasks, return_exceptions=True)

            for event, results in zip(events, all_results):
                if isinstance(results, Exception):
                    logger.error(f"Error processing event {event.event_id}: {results}")
                    results_map[event.event_id] = []
                else:
                    results_map[event.event_id] = results
        else:
            for event in events:
                try:
                    results = await self.process_event(event)
                    results_map[event.event_id] = results
                except Exception as e:
                    logger.error(f"Error processing event {event.event_id}: {e}")
                    results_map[event.event_id] = []

        return results_map

    def _find_matching_rules(self, event: SSOEvent) -> List[TriggerRule]:
        """
        Find trigger rules matching the event.

        Args:
            event: SSOEvent to match

        Returns:
            List of matching TriggerRule objects
        """
        matching_rules = []

        for rule in self._rules:
            # Skip disabled rules
            if not rule.enabled:
                continue

            # Check event type match
            if event.event_type not in rule.event_types:
                continue

            # Check optional condition
            if rule.condition and not rule.condition(event):
                continue

            matching_rules.append(rule)

        return matching_rules

    def _transform_event_to_input(
        self,
        event: SSOEvent,
        rule: TriggerRule
    ) -> Dict[str, Any]:
        """
        Transform event data to workflow input.

        Args:
            event: SSOEvent to transform
            rule: TriggerRule with transformer function

        Returns:
            Input data dictionary for workflow
        """
        if rule.input_transformer:
            return rule.input_transformer(event)

        # Default transformation
        return {
            'event_id': event.event_id,
            'event_type': event.event_type,
            'user_id': event.user_id,
            'user_email': event.user_email,
            'timestamp': event.timestamp
        }

    def get_workflows_for_event(self, event_id: str) -> List[str]:
        """
        Get workflow execution IDs triggered by an event.

        Args:
            event_id: Event identifier

        Returns:
            List of execution IDs
        """
        return self._event_workflow_map.get(event_id, [])

    def get_event_history(
        self,
        event_type: Optional[str] = None,
        user_id: Optional[str] = None,
        limit: int = 100
    ) -> List[SSOEvent]:
        """
        Get event processing history with optional filters.

        Args:
            event_type: Filter by event type
            user_id: Filter by user ID
            limit: Maximum number of events to return

        Returns:
            List of SSOEvent objects
        """
        events = self._event_history

        if event_type:
            events = [e for e in events if e.event_type == event_type]

        if user_id:
            events = [e for e in events if e.user_id == user_id]

        return events[-limit:]

    async def simulate_event(
        self,
        event_type: str,
        user_id: str = 'user123',
        user_email: str = 'test@example.com',
        metadata: Optional[Dict[str, Any]] = None
    ) -> List[ExecutionResult]:
        """
        Simulate an SSO event (useful for testing).

        Args:
            event_type: Type of event to simulate
            user_id: User ID
            user_email: User email
            metadata: Additional event metadata

        Returns:
            List of ExecutionResult objects
        """
        event = SSOEvent(
            event_id=f"sim_{datetime.utcnow().timestamp()}",
            event_type=event_type,
            timestamp=datetime.utcnow().isoformat(),
            user_id=user_id,
            user_email=user_email,
            client_ip='192.168.1.100',
            user_agent='Mock Agent/1.0',
            metadata=metadata or {}
        )

        logger.info(f"Simulating event: {event_type}")
        return await self.process_event(event)

    async def close(self):
        """Close trigger and underlying executor"""
        await self.executor.close()
        logger.info("EventTrigger closed")


# Example usage
if __name__ == '__main__':
    async def main():
        # Initialize event trigger in mock mode
        trigger = EventTrigger(mock_mode=True)

        print("\n=== Configured Trigger Rules ===")
        for rule in trigger.list_rules():
            print(f"  - {rule.rule_id}: {rule.flow_id}")
            print(f"    Event types: {', '.join(rule.event_types)}")

        try:
            # Simulate various SSO events
            print("\n\n=== Simulating SSO Events ===")

            # 1. New user created
            print("\n1. Simulating USER_CREATED event...")
            results = await trigger.simulate_event(
                event_type=SSOEventType.USER_CREATED.value,
                user_id='user001',
                user_email='john.doe@example.com',
                metadata={'department': 'Engineering', 'manager': 'manager123'}
            )
            print(f"   Triggered {len(results)} workflows:")
            for r in results:
                print(f"     - {r.flow_id} [{r.status}]")

            # 2. Login failure due to MFA not enrolled
            print("\n2. Simulating LOGIN_FAILURE event (MFA not enrolled)...")
            results = await trigger.simulate_event(
                event_type=SSOEventType.LOGIN_FAILURE.value,
                user_id='user002',
                user_email='jane.smith@example.com',
                metadata={'reason': 'mfa_not_enrolled'}
            )
            print(f"   Triggered {len(results)} workflows:")
            for r in results:
                print(f"     - {r.flow_id} [{r.status}]")

            # 3. User deactivated
            print("\n3. Simulating USER_DEACTIVATED event...")
            results = await trigger.simulate_event(
                event_type=SSOEventType.USER_DEACTIVATED.value,
                user_id='user003',
                user_email='bob.johnson@example.com',
                metadata={'reason': 'termination', 'effective_date': '2025-12-15'}
            )
            print(f"   Triggered {len(results)} workflows:")
            for r in results:
                print(f"     - {r.flow_id} [{r.status}]")

            # 4. Application access granted
            print("\n4. Simulating APP_ACCESS_GRANTED event...")
            results = await trigger.simulate_event(
                event_type=SSOEventType.APP_ACCESS_GRANTED.value,
                user_id='user004',
                user_email='alice.williams@example.com',
                metadata={'app_id': 'app_salesforce', 'app_name': 'Salesforce'}
            )
            print(f"   Triggered {len(results)} workflows:")
            for r in results:
                print(f"     - {r.flow_id} [{r.status}]")

            # Show event history
            print("\n\n=== Event History ===")
            history = trigger.get_event_history(limit=10)
            for event in history:
                print(f"  - {event.event_type} (user: {event.user_email})")
                workflows = trigger.get_workflows_for_event(event.event_id)
                if workflows:
                    print(f"    Triggered workflows: {', '.join(workflows)}")

            # Show execution statistics
            print("\n\n=== Execution Statistics ===")
            print(f"Total events processed: {len(trigger.get_event_history())}")
            print(f"Overall workflow success rate: {trigger.executor.get_success_rate():.1f}%")

        finally:
            await trigger.close()

    # Run the example
    asyncio.run(main())
