"""
Okta Workflows API Connector

v1.1 Enhancement - December 2025
Provides connectivity to Okta Workflows API for executing and managing automated workflows.

Features:
- Authenticate with Okta Workflows API
- Invoke workflow flows via API endpoints
- Query workflow execution history
- Retrieve flow metadata and configuration
- Mock mode for demonstrations without live API calls
"""

import os
import asyncio
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime
from enum import Enum
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry


# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class WorkflowStatus(Enum):
    """Workflow execution status enumeration"""
    PENDING = "pending"
    RUNNING = "running"
    SUCCESS = "success"
    FAILED = "failed"
    CANCELLED = "cancelled"


class OktaWorkflowsConnector:
    """
    Connector for Okta Workflows API.

    This class provides methods to interact with Okta Workflows including:
    - Flow invocation
    - Status monitoring
    - History retrieval
    - Mock mode for demonstrations

    Attributes:
        org_url (str): Okta organization URL
        api_token (str): Okta API token for authentication
        workflows_url (str): Okta Workflows API endpoint
        mock_mode (bool): Enable mock mode for demos
    """

    def __init__(
        self,
        org_url: Optional[str] = None,
        api_token: Optional[str] = None,
        mock_mode: bool = False
    ):
        """
        Initialize Okta Workflows connector.

        Args:
            org_url: Okta organization URL (defaults to OKTA_ORG_URL env var)
            api_token: Okta API token (defaults to OKTA_API_TOKEN env var)
            mock_mode: Enable mock mode for demonstrations
        """
        self.org_url = org_url or os.getenv('OKTA_ORG_URL')
        self.api_token = api_token or os.getenv('OKTA_API_TOKEN')
        self.mock_mode = mock_mode

        if not self.mock_mode and (not self.org_url or not self.api_token):
            raise ValueError(
                "OKTA_ORG_URL and OKTA_API_TOKEN must be set in environment "
                "or mock_mode must be enabled"
            )

        # Okta Workflows API endpoint
        self.workflows_url = f"{self.org_url}/api/flo/v1" if self.org_url else None

        # Configure HTTP session with retry logic
        self.session = self._create_session()

        logger.info(
            f"OktaWorkflowsConnector initialized "
            f"(mock_mode={'enabled' if mock_mode else 'disabled'})"
        )

    def _create_session(self) -> requests.Session:
        """
        Create HTTP session with retry logic and authentication.

        Returns:
            Configured requests.Session object
        """
        session = requests.Session()

        # Configure retry strategy
        retry_strategy = Retry(
            total=3,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["HEAD", "GET", "POST", "PUT", "DELETE"]
        )

        adapter = HTTPAdapter(max_retries=retry_strategy)
        session.mount("https://", adapter)
        session.mount("http://", adapter)

        # Set default headers
        if not self.mock_mode:
            session.headers.update({
                'Authorization': f'SSWS {self.api_token}',
                'Content-Type': 'application/json',
                'Accept': 'application/json'
            })

        return session

    async def invoke_flow(
        self,
        flow_id: str,
        input_data: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Invoke a workflow flow by ID.

        Args:
            flow_id: Unique identifier for the workflow flow
            input_data: Input parameters for the flow execution

        Returns:
            Dictionary containing execution ID and initial status

        Raises:
            Exception: If flow invocation fails
        """
        if self.mock_mode:
            return self._mock_invoke_flow(flow_id, input_data)

        endpoint = f"{self.workflows_url}/flows/{flow_id}/invoke"
        payload = input_data or {}

        try:
            logger.info(f"Invoking flow {flow_id}")
            response = await asyncio.to_thread(
                self.session.post,
                endpoint,
                json=payload,
                timeout=30
            )
            response.raise_for_status()

            result = response.json()
            logger.info(f"Flow {flow_id} invoked successfully: {result.get('execution_id')}")

            return result

        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to invoke flow {flow_id}: {e}")
            raise Exception(f"Flow invocation failed: {e}")

    async def get_flow_status(self, execution_id: str) -> Dict[str, Any]:
        """
        Get the status of a workflow execution.

        Args:
            execution_id: Execution ID returned from invoke_flow

        Returns:
            Dictionary containing execution status and details
        """
        if self.mock_mode:
            return self._mock_get_flow_status(execution_id)

        endpoint = f"{self.workflows_url}/executions/{execution_id}"

        try:
            response = await asyncio.to_thread(
                self.session.get,
                endpoint,
                timeout=30
            )
            response.raise_for_status()

            return response.json()

        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to get flow status for {execution_id}: {e}")
            raise Exception(f"Status retrieval failed: {e}")

    async def list_flows(self, filter_type: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        List available workflow flows.

        Args:
            filter_type: Optional filter for flow type (e.g., 'remediation', 'lifecycle')

        Returns:
            List of flow metadata dictionaries
        """
        if self.mock_mode:
            return self._mock_list_flows(filter_type)

        endpoint = f"{self.workflows_url}/flows"
        params = {'type': filter_type} if filter_type else {}

        try:
            response = await asyncio.to_thread(
                self.session.get,
                endpoint,
                params=params,
                timeout=30
            )
            response.raise_for_status()

            return response.json().get('flows', [])

        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to list flows: {e}")
            raise Exception(f"Flow listing failed: {e}")

    async def get_execution_history(
        self,
        flow_id: str,
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """
        Get execution history for a specific flow.

        Args:
            flow_id: Workflow flow ID
            limit: Maximum number of executions to retrieve

        Returns:
            List of execution history records
        """
        if self.mock_mode:
            return self._mock_get_execution_history(flow_id, limit)

        endpoint = f"{self.workflows_url}/flows/{flow_id}/executions"
        params = {'limit': limit}

        try:
            response = await asyncio.to_thread(
                self.session.get,
                endpoint,
                params=params,
                timeout=30
            )
            response.raise_for_status()

            return response.json().get('executions', [])

        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to get execution history for {flow_id}: {e}")
            raise Exception(f"History retrieval failed: {e}")

    # Mock mode methods for demonstrations

    def _mock_invoke_flow(
        self,
        flow_id: str,
        input_data: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Mock flow invocation for demo mode"""
        execution_id = f"exec_{flow_id}_{datetime.utcnow().timestamp()}"
        logger.info(f"[MOCK] Invoked flow {flow_id} -> {execution_id}")

        return {
            'execution_id': execution_id,
            'flow_id': flow_id,
            'status': WorkflowStatus.RUNNING.value,
            'started_at': datetime.utcnow().isoformat(),
            'input': input_data or {}
        }

    def _mock_get_flow_status(self, execution_id: str) -> Dict[str, Any]:
        """Mock flow status retrieval for demo mode"""
        logger.info(f"[MOCK] Getting status for execution {execution_id}")

        return {
            'execution_id': execution_id,
            'status': WorkflowStatus.SUCCESS.value,
            'started_at': datetime.utcnow().isoformat(),
            'completed_at': datetime.utcnow().isoformat(),
            'duration_ms': 1234,
            'output': {
                'result': 'success',
                'actions_completed': 5
            }
        }

    def _mock_list_flows(self, filter_type: Optional[str]) -> List[Dict[str, Any]]:
        """Mock flow listing for demo mode"""
        logger.info(f"[MOCK] Listing flows (filter: {filter_type})")

        mock_flows = [
            {
                'flow_id': 'flow_new_hire_onboarding',
                'name': 'New Hire Onboarding',
                'type': 'lifecycle',
                'description': 'Automate new employee provisioning and access setup',
                'enabled': True
            },
            {
                'flow_id': 'flow_offboarding',
                'name': 'Employee Offboarding',
                'type': 'lifecycle',
                'description': 'Revoke access and archive user data',
                'enabled': True
            },
            {
                'flow_id': 'flow_mfa_remediation',
                'name': 'MFA Enrollment Remediation',
                'type': 'remediation',
                'description': 'Automatically enroll users in MFA',
                'enabled': True
            },
            {
                'flow_id': 'flow_access_request',
                'name': 'Application Access Request',
                'type': 'lifecycle',
                'description': 'Process and approve application access requests',
                'enabled': True
            },
            {
                'flow_id': 'flow_password_expiry',
                'name': 'Password Expiry Notification',
                'type': 'remediation',
                'description': 'Notify users before password expiration',
                'enabled': True
            }
        ]

        if filter_type:
            mock_flows = [f for f in mock_flows if f['type'] == filter_type]

        return mock_flows

    def _mock_get_execution_history(
        self,
        flow_id: str,
        limit: int
    ) -> List[Dict[str, Any]]:
        """Mock execution history for demo mode"""
        logger.info(f"[MOCK] Getting execution history for {flow_id}")

        return [
            {
                'execution_id': f'exec_{flow_id}_001',
                'status': WorkflowStatus.SUCCESS.value,
                'started_at': '2025-12-01T10:00:00Z',
                'completed_at': '2025-12-01T10:00:05Z',
                'duration_ms': 5000
            },
            {
                'execution_id': f'exec_{flow_id}_002',
                'status': WorkflowStatus.SUCCESS.value,
                'started_at': '2025-12-02T14:30:00Z',
                'completed_at': '2025-12-02T14:30:03Z',
                'duration_ms': 3000
            },
            {
                'execution_id': f'exec_{flow_id}_003',
                'status': WorkflowStatus.FAILED.value,
                'started_at': '2025-12-03T09:15:00Z',
                'completed_at': '2025-12-03T09:15:10Z',
                'duration_ms': 10000,
                'error': 'Timeout waiting for external API'
            }
        ][:limit]

    async def close(self):
        """Close the HTTP session"""
        if hasattr(self, 'session'):
            await asyncio.to_thread(self.session.close)
            logger.info("OktaWorkflowsConnector session closed")


# Example usage
if __name__ == '__main__':
    async def main():
        # Initialize in mock mode for demonstration
        connector = OktaWorkflowsConnector(mock_mode=True)

        try:
            # List available flows
            print("\n=== Available Workflows ===")
            flows = await connector.list_flows()
            for flow in flows:
                print(f"  - {flow['name']} ({flow['flow_id']}): {flow['description']}")

            # Invoke a flow
            print("\n=== Invoking Onboarding Flow ===")
            result = await connector.invoke_flow(
                'flow_new_hire_onboarding',
                input_data={
                    'user_id': 'user123',
                    'first_name': 'John',
                    'last_name': 'Doe',
                    'email': 'john.doe@example.com'
                }
            )
            print(f"Execution ID: {result['execution_id']}")
            print(f"Status: {result['status']}")

            # Check status
            print("\n=== Checking Execution Status ===")
            status = await connector.get_flow_status(result['execution_id'])
            print(f"Status: {status['status']}")
            print(f"Duration: {status.get('duration_ms')}ms")

            # Get execution history
            print("\n=== Execution History ===")
            history = await connector.get_execution_history('flow_new_hire_onboarding')
            for execution in history:
                print(f"  - {execution['execution_id']}: {execution['status']}")

        finally:
            await connector.close()

    # Run the example
    asyncio.run(main())
