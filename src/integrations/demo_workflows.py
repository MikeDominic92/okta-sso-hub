"""
Okta Workflows Integration Demo

v1.1 Enhancement - December 2025
Demonstrates the complete Okta Workflows integration in action.

This demo script showcases:
- Workflow connector usage
- Flow execution and monitoring
- Event-driven workflow triggering
- Complete integration workflow
"""

import asyncio
import logging
from datetime import datetime

from okta_workflows_connector import OktaWorkflowsConnector
from flow_executor import FlowExecutor
from event_trigger import EventTrigger, SSOEvent, SSOEventType


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


async def demo_connector():
    """Demonstrate the Okta Workflows Connector"""
    print("\n" + "=" * 70)
    print("DEMO 1: Okta Workflows Connector")
    print("=" * 70)

    connector = OktaWorkflowsConnector(mock_mode=True)

    try:
        # List available flows
        print("\n--- Available Workflow Flows ---")
        flows = await connector.list_flows()
        for flow in flows:
            print(f"  [{flow['type']:12}] {flow['name']}")
            print(f"                  {flow['description']}")

        # Invoke a specific flow
        print("\n--- Invoking New Hire Onboarding Flow ---")
        result = await connector.invoke_flow(
            'flow_new_hire_onboarding',
            input_data={
                'user_id': 'user_demo_001',
                'first_name': 'Sarah',
                'last_name': 'Chen',
                'email': 'sarah.chen@example.com',
                'department': 'Product Management'
            }
        )
        print(f"  Execution ID: {result['execution_id']}")
        print(f"  Status: {result['status']}")

        # Check execution status
        print("\n--- Checking Execution Status ---")
        status = await connector.get_flow_status(result['execution_id'])
        print(f"  Status: {status['status']}")
        print(f"  Duration: {status.get('duration_ms', 'N/A')}ms")
        if status.get('output'):
            print(f"  Output: {status['output']}")

        # Get execution history
        print("\n--- Recent Execution History ---")
        history = await connector.get_execution_history('flow_new_hire_onboarding', limit=3)
        for execution in history:
            print(f"  {execution['execution_id']}: {execution['status']} "
                  f"({execution.get('duration_ms', 'N/A')}ms)")

    finally:
        await connector.close()


async def demo_executor():
    """Demonstrate the Flow Executor"""
    print("\n" + "=" * 70)
    print("DEMO 2: Flow Executor with Callbacks")
    print("=" * 70)

    executor = FlowExecutor(mock_mode=True, default_timeout=60, poll_interval=1)

    # Register callbacks
    def on_flow_start(result):
        print(f"\n  >> STARTED: {result.flow_id}")

    def on_flow_complete(result):
        print(f"  >> COMPLETED: {result.flow_id} in {result.duration_ms}ms")

    def on_flow_error(result):
        print(f"  >> FAILED: {result.flow_id} - {result.error}")

    executor.on_start(on_flow_start)
    executor.on_complete(on_flow_complete)
    executor.on_error(on_flow_error)

    try:
        # Execute single flow with monitoring
        print("\n--- Single Flow Execution ---")
        result = await executor.execute_flow(
            'flow_mfa_remediation',
            input_data={'user_id': 'user_demo_002', 'user_email': 'john.doe@example.com'}
        )

        # Execute multiple flows in parallel
        print("\n--- Parallel Multi-Flow Execution ---")
        flows = [
            {'flow_id': 'flow_new_hire_onboarding', 'input_data': {'user_id': 'user_003'}},
            {'flow_id': 'flow_access_request', 'input_data': {'user_id': 'user_003', 'app_id': 'app_slack'}},
            {'flow_id': 'flow_password_expiry', 'input_data': {'user_id': 'user_003'}},
        ]

        results = await executor.execute_multiple_flows(flows, parallel=True)

        # Show statistics
        print("\n--- Execution Statistics ---")
        print(f"  Total executions: {len(executor.get_execution_history())}")
        print(f"  Success rate: {executor.get_success_rate():.1f}%")

        # Show history by flow
        print("\n--- Execution History by Flow ---")
        for flow_id in ['flow_new_hire_onboarding', 'flow_mfa_remediation']:
            history = executor.get_execution_history(flow_id=flow_id)
            if history:
                print(f"  {flow_id}: {len(history)} executions")

    finally:
        await executor.close()


async def demo_event_trigger():
    """Demonstrate the Event Trigger System"""
    print("\n" + "=" * 70)
    print("DEMO 3: SSO Event-Driven Workflow Triggering")
    print("=" * 70)

    trigger = EventTrigger(mock_mode=True)

    try:
        # Show configured rules
        print("\n--- Configured Trigger Rules ---")
        for rule in trigger.list_rules(enabled_only=True):
            print(f"  {rule.rule_id}")
            print(f"    Flow: {rule.flow_id}")
            print(f"    Events: {', '.join(rule.event_types)}")

        # Simulate various SSO events
        print("\n--- Simulating SSO Events ---")

        # Event 1: New user created
        print("\n  1. USER_CREATED Event")
        results = await trigger.simulate_event(
            event_type=SSOEventType.USER_CREATED.value,
            user_id='user_new_001',
            user_email='emily.wong@example.com',
            metadata={'department': 'Engineering', 'title': 'Senior Engineer'}
        )
        print(f"     Triggered {len(results)} workflow(s)")

        # Event 2: Login failure with MFA issue
        print("\n  2. LOGIN_FAILURE Event (MFA not enrolled)")
        results = await trigger.simulate_event(
            event_type=SSOEventType.LOGIN_FAILURE.value,
            user_id='user_existing_002',
            user_email='alex.kim@example.com',
            metadata={'reason': 'mfa_not_enrolled', 'attempts': 3}
        )
        print(f"     Triggered {len(results)} workflow(s)")

        # Event 3: User deactivated
        print("\n  3. USER_DEACTIVATED Event")
        results = await trigger.simulate_event(
            event_type=SSOEventType.USER_DEACTIVATED.value,
            user_id='user_leaving_003',
            user_email='chris.taylor@example.com',
            metadata={'reason': 'termination', 'last_day': '2025-12-31'}
        )
        print(f"     Triggered {len(results)} workflow(s)")

        # Event 4: Application access granted
        print("\n  4. APP_ACCESS_GRANTED Event")
        results = await trigger.simulate_event(
            event_type=SSOEventType.APP_ACCESS_GRANTED.value,
            user_id='user_existing_004',
            user_email='morgan.lee@example.com',
            metadata={'app_id': 'app_salesforce', 'app_name': 'Salesforce CRM'}
        )
        print(f"     Triggered {len(results)} workflow(s)")

        # Show event-workflow correlation
        print("\n--- Event-Workflow Correlation ---")
        event_history = trigger.get_event_history(limit=10)
        for event in event_history:
            workflows = trigger.get_workflows_for_event(event.event_id)
            print(f"  {event.event_type}")
            print(f"    User: {event.user_email}")
            if workflows:
                print(f"    Triggered: {len(workflows)} workflow execution(s)")

        # Show overall statistics
        print("\n--- Overall Statistics ---")
        print(f"  Total events processed: {len(trigger.get_event_history())}")
        print(f"  Workflow success rate: {trigger.executor.get_success_rate():.1f}%")

    finally:
        await trigger.close()


async def demo_complete_integration():
    """Demonstrate complete integration workflow"""
    print("\n" + "=" * 70)
    print("DEMO 4: Complete Integration Workflow")
    print("=" * 70)

    print("\nScenario: New employee joins the company")
    print("-" * 70)

    trigger = EventTrigger(mock_mode=True)

    try:
        # Step 1: HR system creates user account
        print("\nStep 1: HR creates user account in Okta")
        event = SSOEvent(
            event_id='evt_complete_001',
            event_type=SSOEventType.USER_CREATED.value,
            timestamp=datetime.utcnow().isoformat(),
            user_id='00u_new_employee',
            user_email='jamie.rivera@example.com',
            metadata={
                'first_name': 'Jamie',
                'last_name': 'Rivera',
                'department': 'Sales',
                'title': 'Account Executive',
                'manager': 'manager_456',
                'start_date': '2025-12-15'
            }
        )

        print(f"  Created user: {event.user_email}")
        print(f"  Department: {event.metadata['department']}")
        print(f"  Start date: {event.metadata['start_date']}")

        # Step 2: Event triggers onboarding workflow
        print("\nStep 2: Process event and trigger onboarding workflow")
        results = await trigger.process_event(event)

        for result in results:
            print(f"  Workflow: {result.flow_id}")
            print(f"  Execution: {result.execution_id}")
            print(f"  Status: {result.status}")
            print(f"  Duration: {result.duration_ms}ms")

        # Step 3: Show what the workflow would do
        print("\nStep 3: Onboarding workflow actions (simulated)")
        print("  - Provisioned access to:")
        print("    * Email (Microsoft 365)")
        print("    * Slack workspace")
        print("    * Salesforce CRM")
        print("    * Company intranet")
        print("  - Created accounts in:")
        print("    * Active Directory")
        print("    * HR system")
        print("  - Sent notifications to:")
        print("    * New employee (welcome email)")
        print("    * Manager (new hire alert)")
        print("    * IT team (equipment request)")
        print("  - Enrolled in security training")
        print("  - Added to department distribution lists")

        # Step 4: Show correlation
        print("\nStep 4: Event-workflow correlation")
        workflows = trigger.get_workflows_for_event(event.event_id)
        print(f"  Event {event.event_id} triggered {len(workflows)} workflow execution(s)")

        print("\n" + "-" * 70)
        print("Complete integration workflow finished successfully!")

    finally:
        await trigger.close()


async def main():
    """Run all demonstrations"""
    print("\n" + "=" * 70)
    print("OKTA WORKFLOWS INTEGRATION v1.1 - DEMONSTRATION")
    print("December 2025 Enhancement")
    print("=" * 70)

    await demo_connector()
    await demo_executor()
    await demo_event_trigger()
    await demo_complete_integration()

    print("\n" + "=" * 70)
    print("All demonstrations completed successfully!")
    print("=" * 70)
    print("\nKey Takeaways:")
    print("  - Okta Workflows API integration is fully functional")
    print("  - Flow execution with monitoring and analytics works seamlessly")
    print("  - Event-driven triggering automates identity lifecycle workflows")
    print("  - Mock mode enables demonstrations without live API access")
    print("  - Complete correlation between SSO events and workflow executions")
    print("\nNext Steps:")
    print("  - Configure with your Okta org (set mock_mode=False)")
    print("  - Import workflow templates from automation/workflows/")
    print("  - Customize trigger rules for your specific use cases")
    print("  - Integrate with your SSO applications")
    print("\n")


if __name__ == '__main__':
    asyncio.run(main())
