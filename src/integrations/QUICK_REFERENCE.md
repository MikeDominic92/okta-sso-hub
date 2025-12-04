# Okta Workflows Integration - Quick Reference

**v1.1.0 - December 2025**

## Import Statements

```python
# Main module imports
from src.integrations import (
    OktaWorkflowsConnector,
    FlowExecutor,
    EventTrigger
)

# Additional imports for advanced usage
from src.integrations.event_trigger import (
    SSOEvent,
    SSOEventType,
    TriggerRule
)

from src.integrations.flow_executor import (
    ExecutionResult,
    ExecutionError
)

from src.integrations.okta_workflows_connector import (
    WorkflowStatus
)
```

## Quick Start Examples

### 1. Execute a Workflow (Simple)

```python
import asyncio
from src.integrations import FlowExecutor

async def main():
    executor = FlowExecutor(mock_mode=True)

    result = await executor.execute_flow(
        'flow_new_hire_onboarding',
        input_data={'user_id': 'user123'}
    )

    print(f"Status: {result.status}")
    await executor.close()

asyncio.run(main())
```

### 2. Event-Driven Trigger (Simple)

```python
import asyncio
from src.integrations import EventTrigger
from src.integrations.event_trigger import SSOEventType

async def main():
    trigger = EventTrigger(mock_mode=True)

    results = await trigger.simulate_event(
        event_type=SSOEventType.USER_CREATED.value,
        user_id='user123',
        user_email='user@example.com'
    )

    print(f"Triggered {len(results)} workflows")
    await trigger.close()

asyncio.run(main())
```

### 3. Low-Level Connector (Simple)

```python
import asyncio
from src.integrations import OktaWorkflowsConnector

async def main():
    connector = OktaWorkflowsConnector(mock_mode=True)

    # List flows
    flows = await connector.list_flows()

    # Invoke flow
    result = await connector.invoke_flow(
        'flow_new_hire_onboarding',
        input_data={'user_id': 'user123'}
    )

    await connector.close()

asyncio.run(main())
```

## Common Patterns

### Pattern: Fire-and-Forget

```python
# Execute without waiting
result = await executor.execute_flow(
    'flow_notification',
    wait_for_completion=False
)
# Returns immediately with execution_id
```

### Pattern: Wait for Completion

```python
# Wait for workflow to complete
result = await executor.execute_flow(
    'flow_critical_operation',
    wait_for_completion=True,
    timeout=120
)
# Returns when complete or timeout
```

### Pattern: Parallel Execution

```python
flows = [
    {'flow_id': 'flow_email', 'input_data': {'to': 'user@example.com'}},
    {'flow_id': 'flow_slack', 'input_data': {'channel': '#general'}},
]

results = await executor.execute_multiple_flows(flows, parallel=True)
```

### Pattern: Sequential Execution

```python
results = await executor.execute_multiple_flows(flows, parallel=False)
```

### Pattern: With Callbacks

```python
executor = FlowExecutor(mock_mode=True)

executor.on_start(lambda r: print(f"Started: {r.flow_id}"))
executor.on_complete(lambda r: print(f"Done: {r.flow_id}"))
executor.on_error(lambda r: print(f"Error: {r.error}"))

result = await executor.execute_flow('flow_id', input_data={})
```

### Pattern: Event Processing

```python
from src.integrations.event_trigger import SSOEvent

event = SSOEvent(
    event_id='evt_001',
    event_type='user.lifecycle.create',
    timestamp='2025-12-04T10:00:00Z',
    user_id='00u123456',
    user_email='user@example.com',
    metadata={'department': 'Engineering'}
)

results = await trigger.process_event(event)
```

### Pattern: Batch Event Processing

```python
events = [event1, event2, event3]
results_map = await trigger.process_events_batch(events, parallel=True)

for event_id, results in results_map.items():
    print(f"Event {event_id}: {len(results)} workflows")
```

### Pattern: Custom Trigger Rule

```python
from src.integrations.event_trigger import TriggerRule

rule = TriggerRule(
    rule_id='rule_custom',
    event_types=['user.authentication.sso.login.failure'],
    flow_id='flow_security_alert',
    condition=lambda event: event.metadata.get('attempts') > 3,
    input_transformer=lambda event: {
        'user_id': event.user_id,
        'attempts': event.metadata.get('attempts')
    }
)

trigger.add_rule(rule)
```

## Configuration Cheat Sheet

### Environment Variables

```bash
# Required
export OKTA_ORG_URL=https://dev-12345678.okta.com
export OKTA_API_TOKEN=your_token_here

# Optional
export OKTA_WORKFLOWS_TIMEOUT=300
export OKTA_WORKFLOWS_POLL_INTERVAL=2
```

### Initialization Options

```python
# Production mode
connector = OktaWorkflowsConnector(
    org_url='https://dev-12345678.okta.com',
    api_token='your_token',
    mock_mode=False
)

executor = FlowExecutor(
    connector=connector,
    default_timeout=300,
    poll_interval=2,
    mock_mode=False
)

trigger = EventTrigger(
    executor=executor,
    mock_mode=False
)
```

```python
# Mock/Demo mode
connector = OktaWorkflowsConnector(mock_mode=True)
executor = FlowExecutor(mock_mode=True)
trigger = EventTrigger(mock_mode=True)
```

## SSO Event Types Quick Reference

### Authentication Events
```python
SSOEventType.LOGIN_SUCCESS.value
SSOEventType.LOGIN_FAILURE.value
SSOEventType.LOGOUT.value
SSOEventType.SESSION_EXPIRED.value
```

### MFA Events
```python
SSOEventType.MFA_ENROLLED.value
SSOEventType.MFA_CHALLENGE.value
SSOEventType.MFA_FAILURE.value
```

### Lifecycle Events
```python
SSOEventType.USER_CREATED.value
SSOEventType.USER_ACTIVATED.value
SSOEventType.USER_DEACTIVATED.value
SSOEventType.USER_SUSPENDED.value
SSOEventType.USER_UNSUSPENDED.value
```

### Access Events
```python
SSOEventType.APP_ACCESS_GRANTED.value
SSOEventType.APP_ACCESS_REVOKED.value
SSOEventType.GROUP_MEMBERSHIP_ADD.value
SSOEventType.GROUP_MEMBERSHIP_REMOVE.value
```

### Password Events
```python
SSOEventType.PASSWORD_CHANGED.value
SSOEventType.PASSWORD_RESET.value
SSOEventType.PASSWORD_EXPIRING.value
```

### Policy Events
```python
SSOEventType.POLICY_VIOLATION.value
SSOEventType.RISKY_LOGIN.value
```

## Workflow Status Values

```python
WorkflowStatus.PENDING.value      # "pending"
WorkflowStatus.RUNNING.value      # "running"
WorkflowStatus.SUCCESS.value      # "success"
WorkflowStatus.FAILED.value       # "failed"
WorkflowStatus.CANCELLED.value    # "cancelled"
```

## Available Workflow Flows (Mock Mode)

```python
'flow_new_hire_onboarding'    # New employee provisioning
'flow_offboarding'            # Employee offboarding
'flow_mfa_remediation'        # MFA enrollment remediation
'flow_access_request'         # Application access request
'flow_password_expiry'        # Password expiry notification
```

## Common Method Signatures

### OktaWorkflowsConnector

```python
await connector.invoke_flow(flow_id: str, input_data: dict) -> dict
await connector.get_flow_status(execution_id: str) -> dict
await connector.list_flows(filter_type: str = None) -> list
await connector.get_execution_history(flow_id: str, limit: int = 50) -> list
await connector.close()
```

### FlowExecutor

```python
await executor.execute_flow(
    flow_id: str,
    input_data: dict = None,
    timeout: int = None,
    wait_for_completion: bool = True
) -> ExecutionResult

await executor.execute_multiple_flows(
    flow_executions: list,
    parallel: bool = True
) -> list[ExecutionResult]

await executor.get_execution_status(execution_id: str) -> ExecutionResult

executor.get_execution_history(
    flow_id: str = None,
    status_filter: str = None
) -> list[ExecutionResult]

executor.get_success_rate(flow_id: str = None) -> float

executor.on_start(callback: callable)
executor.on_complete(callback: callable)
executor.on_error(callback: callable)

await executor.close()
```

### EventTrigger

```python
await trigger.process_event(event: SSOEvent) -> list[ExecutionResult]

await trigger.process_events_batch(
    events: list[SSOEvent],
    parallel: bool = True
) -> dict[str, list[ExecutionResult]]

await trigger.simulate_event(
    event_type: str,
    user_id: str = 'user123',
    user_email: str = 'test@example.com',
    metadata: dict = None
) -> list[ExecutionResult]

trigger.add_rule(rule: TriggerRule)
trigger.remove_rule(rule_id: str) -> bool
trigger.get_rule(rule_id: str) -> TriggerRule
trigger.list_rules(enabled_only: bool = False) -> list[TriggerRule]

trigger.get_workflows_for_event(event_id: str) -> list[str]

trigger.get_event_history(
    event_type: str = None,
    user_id: str = None,
    limit: int = 100
) -> list[SSOEvent]

await trigger.close()
```

## ExecutionResult Properties

```python
result.execution_id: str
result.flow_id: str
result.status: str
result.started_at: str
result.completed_at: str | None
result.duration_ms: int | None
result.input_data: dict
result.output_data: dict
result.error: str | None

result.is_success() -> bool
result.is_failed() -> bool
result.is_terminal() -> bool
```

## Error Handling

```python
from src.integrations.flow_executor import ExecutionError

try:
    result = await executor.execute_flow('flow_id', input_data={})
except ExecutionError as e:
    print(f"Execution failed: {e}")
except Exception as e:
    print(f"Unexpected error: {e}")
```

## Logging

```python
import logging

# Enable debug logging
logging.basicConfig(level=logging.DEBUG)

# Or configure specific logger
logger = logging.getLogger('okta_workflows_connector')
logger.setLevel(logging.DEBUG)
```

## Testing & Demo

```bash
# Run complete demo
cd src/integrations
python demo_workflows.py

# Test individual modules
python okta_workflows_connector.py
python flow_executor.py
python event_trigger.py
```

## Performance Tips

1. **Use parallel execution** for independent workflows
2. **Adjust poll_interval** based on workflow complexity (default: 2s)
3. **Set appropriate timeouts** for long-running workflows (default: 300s)
4. **Use mock_mode** during development to avoid API rate limits
5. **Batch event processing** for high-volume scenarios

## Common Mistakes to Avoid

1. ❌ Forgetting to `await` async functions
2. ❌ Not closing connectors/executors/triggers
3. ❌ Using sync code in async context
4. ❌ Not handling ExecutionError exceptions
5. ❌ Forgetting to set environment variables in production
6. ❌ Using wait_for_completion=True for fire-and-forget scenarios

## Production Checklist

- [ ] Set `mock_mode=False`
- [ ] Configure `OKTA_ORG_URL` and `OKTA_API_TOKEN`
- [ ] Implement proper error handling
- [ ] Set up logging
- [ ] Configure appropriate timeouts
- [ ] Test with actual Okta Workflows
- [ ] Monitor execution success rates
- [ ] Set up alerting for failures

---

**For complete documentation, see:**
- Module README: `src/integrations/README.md`
- Project README: `README.md` (v1.1 section)
- Demo script: `demo_workflows.py`
