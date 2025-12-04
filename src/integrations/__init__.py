"""
Okta Workflows Integration Module

v1.1 Enhancement - December 2025
Provides integration with Okta Workflows for automated identity lifecycle management
and SSO event-driven workflow execution.

This module enables:
- Connection to Okta Workflows API
- Execution of automated remediation workflows
- Identity lifecycle flow orchestration
- Workflow status monitoring and correlation with SSO events
- Mock mode for demonstrations
"""

from .okta_workflows_connector import OktaWorkflowsConnector
from .flow_executor import FlowExecutor
from .event_trigger import EventTrigger

__all__ = [
    'OktaWorkflowsConnector',
    'FlowExecutor',
    'EventTrigger',
]

__version__ = '1.1.0'
__author__ = 'Michael Dominic'
__description__ = 'Okta Workflows automation integration for SSO Hub'
