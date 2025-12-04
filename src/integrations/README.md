# Okta Workflows Integration Module

**v1.1 Enhancement - December 2025**

This module provides comprehensive integration with Okta Workflows for automated identity lifecycle management and SSO event-driven workflow execution.

## Overview

The Okta Workflows Integration enables:
- Direct API connectivity to Okta Workflows
- Automated workflow execution triggered by SSO events
- Identity lifecycle orchestration (onboarding, offboarding, access management)
- Remediation workflows for security and compliance
- Real-time workflow monitoring and analytics
- Event-workflow correlation for audit trails

## Module Structure

```
src/integrations/
├── __init__.py                      # Module initialization
├── okta_workflows_connector.py      # Okta Workflows API connector
├── flow_executor.py                 # Workflow execution orchestrator
├── event_trigger.py                 # SSO event-driven trigger system
├── demo_workflows.py                # Complete integration demonstration
└── README.md                        # This file
```

## Components

### 1. OktaWorkflowsConnector

**File**: `okta_workflows_connector.py`

Low-level connector for Okta Workflows API.

**Features**:
- Authenticate with Okta Workflows API
- Invoke workflow flows
- Query execution status
- Retrieve execution history
- List available flows
- Mock mode for demonstrations

**Example**:
```python
from src.integrations import OktaWorkflowsConnector

connector = OktaWorkflowsConnector(mock_mode=True)

# Invoke a flow
result = await connector.invoke_flow(
    'flow_new_hire_onboarding',
    input_data={'user_id': 'user123', 'email': 'user@example.com'}
)

# Check status
status = await connector.get_flow_status(result['execution_id'])
```

**Key Methods**:
- `invoke_flow(flow_id, input_data)` - Trigger a workflow
- `get_flow_status(execution_id)` - Get execution status
- `list_flows(filter_type)` - List available workflows
- `get_execution_history(flow_id, limit)` - Get execution history

### 2. FlowExecutor

**File**: `flow_executor.py`

High-level orchestration engine for workflow execution.

**Features**:
- Execute workflows with timeout handling
- Monitor execution progress with polling
- Parallel and sequential multi-flow execution
- Execution history and analytics
- Success rate calculation
- Event callbacks (on_start, on_complete, on_error)

**Example**:
```python
from src.integrations import FlowExecutor

executor = FlowExecutor(mock_mode=True, default_timeout=60)

# Register callbacks
executor.on_start(lambda r: print(f"Started: {r.flow_id}"))
executor.on_complete(lambda r: print(f"Completed: {r.flow_id}"))

# Execute single flow
result = await executor.execute_flow(
    'flow_new_hire_onboarding',
    input_data={'user_id': 'user123'},
    wait_for_completion=True
)

# Execute multiple flows in parallel
flows = [
    {'flow_id': 'flow_onboarding', 'input_data': {'user_id': 'user123'}},
    {'flow_id': 'flow_mfa_setup', 'input_data': {'user_id': 'user123'}},
]
results = await executor.execute_multiple_flows(flows, parallel=True)

# Get statistics
print(f"Success rate: {executor.get_success_rate():.1f}%")
```

**Key Methods**:
- `execute_flow(flow_id, input_data, timeout, wait_for_completion)` - Execute workflow
- `execute_multiple_flows(flow_executions, parallel)` - Execute multiple workflows
- `get_execution_status(execution_id)` - Get current status
- `get_execution_history(flow_id, status_filter)` - Get history
- `get_success_rate(flow_id)` - Calculate success rate
- `on_start/on_complete/on_error(callback)` - Register callbacks

### 3. EventTrigger

**File**: `event_trigger.py`

Event-driven workflow trigger system for SSO events.

**Features**:
- Monitor SSO authentication and lifecycle events
- Rule-based workflow triggering
- Event-to-workflow input transformation
- Event-workflow correlation tracking
- Batch event processing
- Event simulation for testing
- Pre-configured rules for common scenarios

**Example**:
```python
from src.integrations import EventTrigger
from src.integrations.event_trigger import SSOEvent, SSOEventType

trigger = EventTrigger(mock_mode=True)

# Process an event
event = SSOEvent(
    event_id='evt_001',
    event_type=SSOEventType.USER_CREATED.value,
    timestamp='2025-12-04T10:00:00Z',
    user_id='00u123456',
    user_email='newuser@company.com',
    metadata={'department': 'Engineering'}
)

results = await trigger.process_event(event)

# Or simulate an event
results = await trigger.simulate_event(
    event_type=SSOEventType.USER_CREATED.value,
    user_id='user123',
    user_email='user@example.com',
    metadata={'department': 'Sales'}
)

# Get event-workflow correlation
workflows = trigger.get_workflows_for_event('evt_001')
```

**Key Methods**:
- `process_event(event)` - Process SSO event and trigger workflows
- `process_events_batch(events, parallel)` - Process multiple events
- `simulate_event(event_type, user_id, user_email, metadata)` - Simulate event
- `add_rule(rule)` - Add trigger rule
- `get_workflows_for_event(event_id)` - Get triggered workflows
- `get_event_history(event_type, user_id, limit)` - Get event history

## Supported SSO Events

### Authentication Events
- `user.authentication.sso.login.success` - Successful SSO login
- `user.authentication.sso.login.failure` - Failed SSO login
- `user.authentication.sso.logout` - SSO logout
- `user.session.expired` - Session expiration

### MFA Events
- `user.mfa.factor.activate` - MFA enrollment
- `user.mfa.factor.challenge` - MFA challenge
- `user.mfa.factor.failure` - MFA failure

### User Lifecycle Events
- `user.lifecycle.create` - User created
- `user.lifecycle.activate` - User activated
- `user.lifecycle.deactivate` - User deactivated
- `user.lifecycle.suspend` - User suspended
- `user.lifecycle.unsuspend` - User unsuspended

### Access Events
- `application.user_membership.add` - App access granted
- `application.user_membership.remove` - App access revoked
- `group.user_membership.add` - Group membership added
- `group.user_membership.remove` - Group membership removed

### Password Events
- `user.account.update_password` - Password changed
- `user.account.reset_password` - Password reset
- `user.password.expiring` - Password expiring soon

### Policy Events
- `policy.violation` - Policy violation
- `user.authentication.risk.detected` - Risky login detected

## Pre-Configured Workflow Triggers

The EventTrigger comes with 5 pre-configured rules:

### 1. New Hire Onboarding
- **Events**: `user.lifecycle.create`, `user.lifecycle.activate`
- **Flow**: `flow_new_hire_onboarding`
- **Actions**: Provision access, create accounts, send notifications

### 2. Employee Offboarding
- **Events**: `user.lifecycle.deactivate`
- **Flow**: `flow_offboarding`
- **Actions**: Revoke access, archive data, notify stakeholders

### 3. MFA Remediation
- **Events**: `user.authentication.sso.login.failure`
- **Condition**: `reason == 'mfa_not_enrolled'`
- **Flow**: `flow_mfa_remediation`
- **Actions**: Auto-enroll in MFA, send setup instructions

### 4. Password Expiry Notification
- **Events**: `user.password.expiring`
- **Flow**: `flow_password_expiry`
- **Actions**: Send notification, provide reset link

### 5. Application Access Request
- **Events**: `application.user_membership.add`
- **Flow**: `flow_access_request`
- **Actions**: Log request, notify manager, provision access

## Configuration

### Environment Variables

```bash
# Required for production mode
OKTA_ORG_URL=https://dev-12345678.okta.com
OKTA_API_TOKEN=your_api_token_here

# Optional settings
OKTA_WORKFLOWS_TIMEOUT=300  # Execution timeout in seconds
OKTA_WORKFLOWS_POLL_INTERVAL=2  # Status polling interval
```

### Mock Mode

For demonstrations and testing, use `mock_mode=True`:

```python
connector = OktaWorkflowsConnector(mock_mode=True)
executor = FlowExecutor(mock_mode=True)
trigger = EventTrigger(mock_mode=True)
```

Mock mode provides:
- Simulated API responses
- Realistic execution times
- Success and failure scenarios
- No actual API calls

## Running the Demo

Execute the complete demonstration:

```bash
cd src/integrations
python demo_workflows.py
```

The demo includes:
1. Okta Workflows Connector demonstration
2. Flow Executor with callbacks
3. SSO Event-Driven triggering
4. Complete integration workflow (end-to-end scenario)

## Usage Examples

### Basic Flow Execution

```python
import asyncio
from src.integrations import FlowExecutor

async def execute_onboarding():
    executor = FlowExecutor(mock_mode=True)

    result = await executor.execute_flow(
        'flow_new_hire_onboarding',
        input_data={
            'user_id': 'user123',
            'first_name': 'John',
            'last_name': 'Doe',
            'email': 'john.doe@example.com',
            'department': 'Engineering'
        },
        wait_for_completion=True
    )

    print(f"Status: {result.status}")
    print(f"Duration: {result.duration_ms}ms")

    await executor.close()

asyncio.run(execute_onboarding())
```

### Event-Driven Workflow

```python
import asyncio
from src.integrations import EventTrigger
from src.integrations.event_trigger import SSOEventType

async def handle_user_creation():
    trigger = EventTrigger(mock_mode=True)

    # Simulate new user creation event
    results = await trigger.simulate_event(
        event_type=SSOEventType.USER_CREATED.value,
        user_id='user123',
        user_email='john.doe@example.com',
        metadata={'department': 'Sales', 'title': 'Account Executive'}
    )

    for result in results:
        print(f"Triggered workflow: {result.flow_id}")
        print(f"Status: {result.status}")

    await trigger.close()

asyncio.run(handle_user_creation())
```

### Custom Trigger Rules

```python
from src.integrations import EventTrigger
from src.integrations.event_trigger import TriggerRule, SSOEventType

trigger = EventTrigger(mock_mode=True)

# Add custom rule
custom_rule = TriggerRule(
    rule_id='rule_custom_security',
    event_types=[SSOEventType.RISKY_LOGIN.value],
    flow_id='flow_security_investigation',
    condition=lambda event: event.metadata.get('risk_level') == 'high',
    input_transformer=lambda event: {
        'user_id': event.user_id,
        'risk_level': event.metadata.get('risk_level'),
        'ip_address': event.client_ip
    }
)

trigger.add_rule(custom_rule)
```

## Architecture Patterns

### 1. Fire-and-Forget
Execute workflow without waiting for completion:

```python
result = await executor.execute_flow(
    'flow_notification',
    wait_for_completion=False
)
# Returns immediately with execution_id
```

### 2. Synchronous Execution
Wait for workflow to complete:

```python
result = await executor.execute_flow(
    'flow_critical_operation',
    wait_for_completion=True,
    timeout=120
)
# Waits until completion or timeout
```

### 3. Parallel Execution
Execute multiple workflows concurrently:

```python
flows = [
    {'flow_id': 'flow_email', 'input_data': {'to': 'user@example.com'}},
    {'flow_id': 'flow_slack', 'input_data': {'channel': '#general'}},
    {'flow_id': 'flow_audit', 'input_data': {'action': 'user_created'}},
]
results = await executor.execute_multiple_flows(flows, parallel=True)
```

### 4. Event-Driven Architecture
Automatically trigger workflows based on events:

```python
trigger = EventTrigger(mock_mode=False)

# Events automatically trigger configured workflows
await trigger.process_event(event)
```

## Error Handling

All components provide comprehensive error handling:

```python
try:
    result = await executor.execute_flow('flow_id', input_data={})
except ExecutionError as e:
    print(f"Execution failed: {e}")
except Exception as e:
    print(f"Unexpected error: {e}")
```

## Logging

All components use Python's logging framework:

```python
import logging

# Enable debug logging
logging.basicConfig(level=logging.DEBUG)

# Or configure specific logger
logger = logging.getLogger('okta_workflows_connector')
logger.setLevel(logging.DEBUG)
```

## Performance Considerations

- **Polling Interval**: Adjust `poll_interval` based on workflow complexity
- **Timeout**: Set appropriate `timeout` values for long-running workflows
- **Parallel Execution**: Use for independent workflows to reduce total time
- **Mock Mode**: Use for development/testing to avoid API rate limits

## Testing

Run the individual module examples:

```bash
# Test connector
python okta_workflows_connector.py

# Test executor
python flow_executor.py

# Test event trigger
python event_trigger.py

# Run complete demo
python demo_workflows.py
```

## Integration with SSO Hub

This module integrates seamlessly with the Okta SSO Hub:

1. **SAML/OIDC Events** → EventTrigger → Workflows
2. **User Provisioning** → FlowExecutor → Onboarding Workflows
3. **Authentication Failures** → EventTrigger → Remediation Workflows
4. **Session Events** → EventTrigger → Security Workflows

## Troubleshooting

### Connection Issues
- Verify `OKTA_ORG_URL` and `OKTA_API_TOKEN` environment variables
- Check network connectivity to Okta
- Ensure API token has required permissions

### Timeout Errors
- Increase `default_timeout` value
- Check workflow complexity
- Verify workflow is not stuck

### Event Not Triggering Workflows
- Verify trigger rules are enabled
- Check event type matches rule configuration
- Test rule conditions with sample events

## Future Enhancements

Planned for v1.2:
- [ ] Webhook receiver for real-time Okta events
- [ ] Advanced workflow chaining
- [ ] Workflow execution dashboard
- [ ] Performance metrics and alerting
- [ ] Workflow template library expansion

## Support

For issues or questions:
- Review module docstrings
- Run demo scripts for examples
- Check main project README.md
- Review CHANGELOG.md for updates

## License

MIT License - See main project LICENSE file

---

**v1.1.0 - December 2025**
*Okta Workflows Integration for automated identity lifecycle management*
