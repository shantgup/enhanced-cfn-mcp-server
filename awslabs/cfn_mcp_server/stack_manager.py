# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""CloudFormation stack management operations."""

import json
import time
from typing import Dict, List, Any, Optional
from awslabs.cfn_mcp_server.aws_client import get_aws_client
from awslabs.cfn_mcp_server.config import config_manager
from botocore.exceptions import ClientError


class StackManager:
    """Manages CloudFormation stack operations."""
    
    def __init__(self, region: str = None, config=None):
        """Initialize the stack manager.
        
        Args:
            region: AWS region for stack operations (defaults to configured default)
            config: Optional configuration manager instance
        """
        self.config = config or config_manager
        self.region = region or self.config.get_config('aws.default_region')
        self.client = get_aws_client('cloudformation', self.region)
    
    async def deploy_stack(
        self,
        stack_name: str,
        template_body: Optional[str] = None,
        template_file: Optional[str] = None,
        parameters: List[Dict[str, str]] = None,
        tags: List[Dict[str, str]] = None,
        capabilities: List[str] = None,
        wait_for_completion: bool = True
    ) -> Dict[str, Any]:
        """Deploy a CloudFormation stack.
        
        Args:
            stack_name: Name of the stack
            template_body: Template content as string
            template_file: Path to template file
            parameters: Stack parameters
            tags: Stack tags
            capabilities: IAM capabilities
            wait_for_completion: Whether to wait for completion
            
        Returns:
            Deployment result information
        """
        try:
            # Get template content
            if template_file:
                with open(template_file, 'r') as f:
                    template_body = f.read()
            elif not template_body:
                raise ValueError("Either template_body or template_file must be provided")
            
            # Check if stack exists
            stack_exists = await self._stack_exists(stack_name)
            
            # Prepare parameters
            deploy_params = {
                'StackName': stack_name,
                'TemplateBody': template_body,
                'Parameters': parameters or [],
                'Tags': tags or [],
                'Capabilities': capabilities or []
            }
            
            # Deploy or update stack
            if stack_exists:
                operation = 'UPDATE'
                try:
                    response = self.client.update_stack(**deploy_params)
                    stack_id = response['StackId']
                except ClientError as e:
                    if 'No updates are to be performed' in str(e):
                        return {
                            'success': True,
                            'operation': 'NO_UPDATE',
                            'message': 'No updates are to be performed on the stack',
                            'stack_name': stack_name
                        }
                    raise
            else:
                operation = 'CREATE'
                response = self.client.create_stack(**deploy_params)
                stack_id = response['StackId']
            
            result = {
                'success': True,
                'operation': operation,
                'stack_name': stack_name,
                'stack_id': stack_id,
                'region': self.region
            }
            
            # Wait for completion if requested
            if wait_for_completion:
                completion_result = await self._wait_for_stack_completion(
                    stack_name, operation
                )
                result.update(completion_result)
            
            return result
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'stack_name': stack_name,
                'operation': operation if 'operation' in locals() else 'UNKNOWN'
            }
    
    async def get_stack_status(
        self,
        stack_name: str,
        include_resources: bool = True,
        include_events: bool = True
    ) -> Dict[str, Any]:
        """Get comprehensive stack status information.
        
        Args:
            stack_name: Name of the stack
            include_resources: Whether to include resource details
            include_events: Whether to include recent events
            
        Returns:
            Stack status information
        """
        try:
            # Get stack information
            stacks_response = self.client.describe_stacks(StackName=stack_name)
            stack = stacks_response['Stacks'][0]
            
            result = {
                'success': True,
                'stack_name': stack_name,
                'stack_status': stack['StackStatus'],
                'creation_time': stack.get('CreationTime'),
                'last_updated_time': stack.get('LastUpdatedTime'),
                'description': stack.get('Description'),
                'parameters': stack.get('Parameters', []),
                'tags': stack.get('Tags', []),
                'outputs': stack.get('Outputs', []),
                'capabilities': stack.get('Capabilities', [])
            }
            
            # Add status reason if available
            if 'StackStatusReason' in stack:
                result['status_reason'] = stack['StackStatusReason']
            
            # Include resources if requested
            if include_resources:
                try:
                    resources_response = self.client.describe_stack_resources(
                        StackName=stack_name
                    )
                    result['resources'] = resources_response['StackResources']
                except ClientError:
                    result['resources'] = []
            
            # Include events if requested
            if include_events:
                try:
                    events_response = self.client.describe_stack_events(
                        StackName=stack_name
                    )
                    # Get the most recent 20 events
                    result['events'] = events_response['StackEvents'][:20]
                except ClientError:
                    result['events'] = []
            
            return result
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'stack_name': stack_name
            }
    
    async def delete_stack(
        self,
        stack_name: str,
        retain_resources: List[str] = None,
        wait_for_completion: bool = True
    ) -> Dict[str, Any]:
        """Delete a CloudFormation stack.
        
        Args:
            stack_name: Name of the stack to delete
            retain_resources: List of logical resource IDs to retain
            wait_for_completion: Whether to wait for deletion completion
            
        Returns:
            Deletion result information
        """
        try:
            delete_params = {'StackName': stack_name}
            
            if retain_resources:
                delete_params['RetainResources'] = retain_resources
            
            self.client.delete_stack(**delete_params)
            
            result = {
                'success': True,
                'operation': 'DELETE',
                'stack_name': stack_name,
                'retained_resources': retain_resources or []
            }
            
            # Wait for completion if requested
            if wait_for_completion:
                completion_result = await self._wait_for_stack_completion(
                    stack_name, 'DELETE'
                )
                result.update(completion_result)
            
            return result
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'stack_name': stack_name,
                'operation': 'DELETE'
            }
    
    async def _stack_exists(self, stack_name: str) -> bool:
        """Check if a stack exists.
        
        Args:
            stack_name: Name of the stack
            
        Returns:
            True if stack exists, False otherwise
        """
        try:
            self.client.describe_stacks(StackName=stack_name)
            return True
        except ClientError as e:
            if 'does not exist' in str(e):
                return False
            raise
    
    async def _wait_for_stack_completion(
        self,
        stack_name: str,
        operation: str,
        timeout_minutes: int = 30
    ) -> Dict[str, Any]:
        """Wait for stack operation to complete.
        
        Args:
            stack_name: Name of the stack
            operation: Operation type (CREATE, UPDATE, DELETE)
            timeout_minutes: Maximum time to wait
            
        Returns:
            Completion status information
        """
        start_time = time.time()
        timeout_seconds = timeout_minutes * 60
        
        # Define completion and failure statuses for each operation
        status_map = {
            'CREATE': {
                'success': ['CREATE_COMPLETE'],
                'failure': ['CREATE_FAILED', 'ROLLBACK_COMPLETE', 'ROLLBACK_FAILED'],
                'in_progress': ['CREATE_IN_PROGRESS', 'ROLLBACK_IN_PROGRESS']
            },
            'UPDATE': {
                'success': ['UPDATE_COMPLETE'],
                'failure': ['UPDATE_FAILED', 'UPDATE_ROLLBACK_COMPLETE', 'UPDATE_ROLLBACK_FAILED'],
                'in_progress': ['UPDATE_IN_PROGRESS', 'UPDATE_ROLLBACK_IN_PROGRESS']
            },
            'DELETE': {
                'success': ['DELETE_COMPLETE'],
                'failure': ['DELETE_FAILED'],
                'in_progress': ['DELETE_IN_PROGRESS']
            }
        }
        
        statuses = status_map.get(operation, status_map['CREATE'])
        
        while time.time() - start_time < timeout_seconds:
            try:
                if operation == 'DELETE':
                    # For delete operations, check if stack still exists
                    try:
                        stack_status = await self.get_stack_status(stack_name, False, False)
                        current_status = stack_status.get('stack_status')
                    except:
                        # Stack no longer exists, deletion complete
                        return {
                            'completion_status': 'SUCCESS',
                            'final_status': 'DELETE_COMPLETE',
                            'duration_seconds': int(time.time() - start_time)
                        }
                else:
                    stack_status = await self.get_stack_status(stack_name, False, False)
                    current_status = stack_status.get('stack_status')
                
                if not current_status:
                    break
                
                if current_status in statuses['success']:
                    return {
                        'completion_status': 'SUCCESS',
                        'final_status': current_status,
                        'duration_seconds': int(time.time() - start_time)
                    }
                elif current_status in statuses['failure']:
                    # Get recent events for failure details
                    events_info = await self._get_failure_events(stack_name)
                    return {
                        'completion_status': 'FAILED',
                        'final_status': current_status,
                        'duration_seconds': int(time.time() - start_time),
                        'failure_events': events_info
                    }
                elif current_status in statuses['in_progress']:
                    # Still in progress, continue waiting
                    time.sleep(10)
                else:
                    # Unknown status
                    break
                    
            except Exception as e:
                if operation == 'DELETE' and 'does not exist' in str(e):
                    # Stack deleted successfully
                    return {
                        'completion_status': 'SUCCESS',
                        'final_status': 'DELETE_COMPLETE',
                        'duration_seconds': int(time.time() - start_time)
                    }
                break
        
        # Timeout reached
        return {
            'completion_status': 'TIMEOUT',
            'final_status': 'UNKNOWN',
            'duration_seconds': int(time.time() - start_time),
            'timeout_minutes': timeout_minutes
        }
    
    async def _get_failure_events(self, stack_name: str) -> List[Dict[str, Any]]:
        """Get failure events for a stack.
        
        Args:
            stack_name: Name of the stack
            
        Returns:
            List of failure events
        """
        try:
            events_response = self.client.describe_stack_events(StackName=stack_name)
            failure_events = []
            
            for event in events_response['StackEvents'][:10]:  # Get last 10 events
                if 'FAILED' in event.get('ResourceStatus', ''):
                    failure_events.append({
                        'timestamp': event.get('Timestamp'),
                        'resource_type': event.get('ResourceType'),
                        'logical_resource_id': event.get('LogicalResourceId'),
                        'resource_status': event.get('ResourceStatus'),
                        'resource_status_reason': event.get('ResourceStatusReason')
                    })
            
            return failure_events
            
        except Exception:
            return []
