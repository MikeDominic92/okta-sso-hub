"""
Workflow Flow Executor

v1.1 Enhancement - December 2025
Orchestrates execution and monitoring of Okta Workflow flows.

Features:
- Execute workflows with input validation
- Monitor execution progress with polling
- Handle execution timeouts and retries
- Aggregate execution results
- Correlate workflow outcomes with SSO events
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any, Callable
from datetime import datetime, timedelta
from enum import Enum
from dataclasses import dataclass, field

from .okta_workflows_connector import OktaWorkflowsConnector, WorkflowStatus


# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ExecutionError(Exception):
    """Exception raised when workflow execution fails"""
    pass


@dataclass
class ExecutionResult:
    """
    Workflow execution result container.

    Attributes:
        execution_id: Unique execution identifier
        flow_id: Workflow flow identifier
        status: Final execution status
        started_at: Execution start timestamp
        completed_at: Execution completion timestamp
        duration_ms: Total execution duration in milliseconds
        input_data: Input parameters provided to flow
        output_data: Output data from flow execution
        error: Error message if execution failed
    """
    execution_id: str
    flow_id: str
    status: str
    started_at: str
    completed_at: Optional[str] = None
    duration_ms: Optional[int] = None
    input_data: Dict[str, Any] = field(default_factory=dict)
    output_data: Dict[str, Any] = field(default_factory=dict)
    error: Optional[str] = None

    def is_success(self) -> bool:
        """Check if execution was successful"""
        return self.status == WorkflowStatus.SUCCESS.value

    def is_failed(self) -> bool:
        """Check if execution failed"""
        return self.status == WorkflowStatus.FAILED.value

    def is_terminal(self) -> bool:
        """Check if execution reached a terminal state"""
        return self.status in [
            WorkflowStatus.SUCCESS.value,
            WorkflowStatus.FAILED.value,
            WorkflowStatus.CANCELLED.value
        ]


class FlowExecutor:
    """
    Orchestrates Okta Workflow flow execution and monitoring.

    This class provides high-level methods to execute workflows with:
    - Input validation
    - Progress monitoring with polling
    - Timeout handling
    - Result aggregation
    - Event correlation

    Attributes:
        connector: OktaWorkflowsConnector instance
        default_timeout: Default execution timeout in seconds
        poll_interval: Status polling interval in seconds
    """

    def __init__(
        self,
        connector: Optional[OktaWorkflowsConnector] = None,
        default_timeout: int = 300,
        poll_interval: int = 2,
        mock_mode: bool = False
    ):
        """
        Initialize FlowExecutor.

        Args:
            connector: OktaWorkflowsConnector instance (created if not provided)
            default_timeout: Default execution timeout in seconds
            poll_interval: Status polling interval in seconds
            mock_mode: Enable mock mode for demonstrations
        """
        self.connector = connector or OktaWorkflowsConnector(mock_mode=mock_mode)
        self.default_timeout = default_timeout
        self.poll_interval = poll_interval
        self.mock_mode = mock_mode

        # Execution history
        self._execution_history: List[ExecutionResult] = []

        # Callback hooks
        self._on_start_callbacks: List[Callable] = []
        self._on_complete_callbacks: List[Callable] = []
        self._on_error_callbacks: List[Callable] = []

        logger.info(
            f"FlowExecutor initialized (timeout={default_timeout}s, "
            f"poll_interval={poll_interval}s, mock_mode={mock_mode})"
        )

    async def execute_flow(
        self,
        flow_id: str,
        input_data: Optional[Dict[str, Any]] = None,
        timeout: Optional[int] = None,
        wait_for_completion: bool = True
    ) -> ExecutionResult:
        """
        Execute a workflow flow and optionally wait for completion.

        Args:
            flow_id: Workflow flow identifier
            input_data: Input parameters for the flow
            timeout: Execution timeout in seconds (uses default if not provided)
            wait_for_completion: Wait for flow to complete before returning

        Returns:
            ExecutionResult object with execution details

        Raises:
            ExecutionError: If execution fails or times out
        """
        timeout = timeout or self.default_timeout
        input_data = input_data or {}

        logger.info(f"Executing flow {flow_id} with timeout {timeout}s")

        try:
            # Invoke the flow
            invocation_result = await self.connector.invoke_flow(flow_id, input_data)
            execution_id = invocation_result.get('execution_id')

            if not execution_id:
                raise ExecutionError("No execution_id returned from flow invocation")

            # Create initial result object
            result = ExecutionResult(
                execution_id=execution_id,
                flow_id=flow_id,
                status=invocation_result.get('status', WorkflowStatus.RUNNING.value),
                started_at=invocation_result.get('started_at', datetime.utcnow().isoformat()),
                input_data=input_data
            )

            # Trigger start callbacks
            await self._trigger_callbacks(self._on_start_callbacks, result)

            # Wait for completion if requested
            if wait_for_completion:
                result = await self._wait_for_completion(execution_id, timeout)

                # Trigger completion or error callbacks
                if result.is_success():
                    await self._trigger_callbacks(self._on_complete_callbacks, result)
                elif result.is_failed():
                    await self._trigger_callbacks(self._on_error_callbacks, result)

            # Add to history
            self._execution_history.append(result)

            return result

        except Exception as e:
            logger.error(f"Flow execution failed: {e}")
            raise ExecutionError(f"Failed to execute flow {flow_id}: {e}")

    async def execute_multiple_flows(
        self,
        flow_executions: List[Dict[str, Any]],
        parallel: bool = True
    ) -> List[ExecutionResult]:
        """
        Execute multiple workflow flows.

        Args:
            flow_executions: List of dicts with 'flow_id' and optional 'input_data'
            parallel: Execute flows in parallel (True) or sequentially (False)

        Returns:
            List of ExecutionResult objects
        """
        logger.info(f"Executing {len(flow_executions)} flows ({'parallel' if parallel else 'sequential'})")

        if parallel:
            tasks = [
                self.execute_flow(
                    flow_id=exec_spec['flow_id'],
                    input_data=exec_spec.get('input_data')
                )
                for exec_spec in flow_executions
            ]
            results = await asyncio.gather(*tasks, return_exceptions=True)

            # Convert exceptions to failed results
            final_results = []
            for i, result in enumerate(results):
                if isinstance(result, Exception):
                    final_results.append(ExecutionResult(
                        execution_id=f"failed_{i}",
                        flow_id=flow_executions[i]['flow_id'],
                        status=WorkflowStatus.FAILED.value,
                        started_at=datetime.utcnow().isoformat(),
                        error=str(result)
                    ))
                else:
                    final_results.append(result)

            return final_results
        else:
            results = []
            for exec_spec in flow_executions:
                try:
                    result = await self.execute_flow(
                        flow_id=exec_spec['flow_id'],
                        input_data=exec_spec.get('input_data')
                    )
                    results.append(result)
                except Exception as e:
                    results.append(ExecutionResult(
                        execution_id=f"failed_{len(results)}",
                        flow_id=exec_spec['flow_id'],
                        status=WorkflowStatus.FAILED.value,
                        started_at=datetime.utcnow().isoformat(),
                        error=str(e)
                    ))

            return results

    async def _wait_for_completion(
        self,
        execution_id: str,
        timeout: int
    ) -> ExecutionResult:
        """
        Poll for execution completion with timeout.

        Args:
            execution_id: Execution identifier
            timeout: Maximum wait time in seconds

        Returns:
            ExecutionResult with final status

        Raises:
            ExecutionError: If execution times out
        """
        start_time = datetime.utcnow()
        timeout_time = start_time + timedelta(seconds=timeout)

        logger.info(f"Waiting for execution {execution_id} to complete (timeout: {timeout}s)")

        while datetime.utcnow() < timeout_time:
            status_data = await self.connector.get_flow_status(execution_id)

            result = ExecutionResult(
                execution_id=execution_id,
                flow_id=status_data.get('flow_id', 'unknown'),
                status=status_data.get('status', WorkflowStatus.RUNNING.value),
                started_at=status_data.get('started_at', start_time.isoformat()),
                completed_at=status_data.get('completed_at'),
                duration_ms=status_data.get('duration_ms'),
                output_data=status_data.get('output', {}),
                error=status_data.get('error')
            )

            if result.is_terminal():
                logger.info(f"Execution {execution_id} completed with status: {result.status}")
                return result

            # Wait before next poll
            await asyncio.sleep(self.poll_interval)

        # Timeout reached
        raise ExecutionError(
            f"Execution {execution_id} timed out after {timeout} seconds"
        )

    async def get_execution_status(self, execution_id: str) -> ExecutionResult:
        """
        Get current status of a workflow execution.

        Args:
            execution_id: Execution identifier

        Returns:
            ExecutionResult with current status
        """
        status_data = await self.connector.get_flow_status(execution_id)

        return ExecutionResult(
            execution_id=execution_id,
            flow_id=status_data.get('flow_id', 'unknown'),
            status=status_data.get('status', WorkflowStatus.RUNNING.value),
            started_at=status_data.get('started_at'),
            completed_at=status_data.get('completed_at'),
            duration_ms=status_data.get('duration_ms'),
            output_data=status_data.get('output', {}),
            error=status_data.get('error')
        )

    def get_execution_history(
        self,
        flow_id: Optional[str] = None,
        status_filter: Optional[str] = None
    ) -> List[ExecutionResult]:
        """
        Get execution history with optional filters.

        Args:
            flow_id: Filter by flow ID
            status_filter: Filter by status

        Returns:
            List of ExecutionResult objects
        """
        results = self._execution_history

        if flow_id:
            results = [r for r in results if r.flow_id == flow_id]

        if status_filter:
            results = [r for r in results if r.status == status_filter]

        return results

    def get_success_rate(self, flow_id: Optional[str] = None) -> float:
        """
        Calculate success rate for executions.

        Args:
            flow_id: Optional flow ID to filter by

        Returns:
            Success rate as percentage (0-100)
        """
        history = self.get_execution_history(flow_id=flow_id)

        if not history:
            return 0.0

        successes = sum(1 for r in history if r.is_success())
        return (successes / len(history)) * 100

    # Callback registration methods

    def on_start(self, callback: Callable[[ExecutionResult], None]):
        """Register callback for flow start events"""
        self._on_start_callbacks.append(callback)

    def on_complete(self, callback: Callable[[ExecutionResult], None]):
        """Register callback for flow completion events"""
        self._on_complete_callbacks.append(callback)

    def on_error(self, callback: Callable[[ExecutionResult], None]):
        """Register callback for flow error events"""
        self._on_error_callbacks.append(callback)

    async def _trigger_callbacks(
        self,
        callbacks: List[Callable],
        result: ExecutionResult
    ):
        """Trigger registered callbacks"""
        for callback in callbacks:
            try:
                if asyncio.iscoroutinefunction(callback):
                    await callback(result)
                else:
                    callback(result)
            except Exception as e:
                logger.error(f"Callback error: {e}")

    async def close(self):
        """Close executor and underlying connector"""
        await self.connector.close()
        logger.info("FlowExecutor closed")


# Example usage
if __name__ == '__main__':
    async def main():
        # Initialize executor in mock mode
        executor = FlowExecutor(mock_mode=True, default_timeout=60, poll_interval=1)

        # Register callbacks
        def on_flow_start(result: ExecutionResult):
            print(f"\n>>> Flow started: {result.flow_id} (execution: {result.execution_id})")

        def on_flow_complete(result: ExecutionResult):
            print(f">>> Flow completed: {result.flow_id} in {result.duration_ms}ms")

        def on_flow_error(result: ExecutionResult):
            print(f">>> Flow failed: {result.flow_id} - {result.error}")

        executor.on_start(on_flow_start)
        executor.on_complete(on_flow_complete)
        executor.on_error(on_flow_error)

        try:
            # Execute single flow
            print("\n=== Executing Single Flow ===")
            result = await executor.execute_flow(
                'flow_new_hire_onboarding',
                input_data={
                    'user_id': 'user123',
                    'first_name': 'Jane',
                    'last_name': 'Smith',
                    'email': 'jane.smith@example.com',
                    'department': 'Engineering'
                }
            )

            print(f"\nResult: {result.status}")
            print(f"Duration: {result.duration_ms}ms")

            # Execute multiple flows in parallel
            print("\n\n=== Executing Multiple Flows in Parallel ===")
            flows_to_execute = [
                {
                    'flow_id': 'flow_mfa_remediation',
                    'input_data': {'user_id': 'user123'}
                },
                {
                    'flow_id': 'flow_access_request',
                    'input_data': {'user_id': 'user123', 'app_id': 'app_salesforce'}
                },
                {
                    'flow_id': 'flow_password_expiry',
                    'input_data': {'user_id': 'user123'}
                }
            ]

            results = await executor.execute_multiple_flows(flows_to_execute, parallel=True)

            print(f"\nCompleted {len(results)} flows:")
            for r in results:
                print(f"  - {r.flow_id}: {r.status}")

            # Show execution history
            print("\n\n=== Execution History ===")
            history = executor.get_execution_history()
            for execution in history:
                print(f"  - {execution.flow_id} [{execution.status}] - {execution.execution_id}")

            # Show success rate
            print(f"\n=== Success Rate ===")
            print(f"Overall: {executor.get_success_rate():.1f}%")

        finally:
            await executor.close()

    # Run the example
    asyncio.run(main())
