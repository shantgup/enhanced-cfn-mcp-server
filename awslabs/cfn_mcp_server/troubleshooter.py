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

"""CloudFormation troubleshooting capabilities - data collection focused."""

import inspect
import json
import time
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from awslabs.cfn_mcp_server.aws_client import get_aws_client
from awslabs.cfn_mcp_server.stack_manager import StackManager
from awslabs.cfn_mcp_server.config import config_manager
from botocore.exceptions import ClientError
import logging

logger = logging.getLogger(__name__)


async def handle_aws_api_call(func, error_value=None, *args, **kwargs):
    """Execute AWS API calls with standardized error handling."""
    try:
        result = func(*args, **kwargs)
        if inspect.iscoroutine(result):
            result = await result
        return result
    except ClientError as e:
        logger.warning(
            f"API error in {func.__name__ if hasattr(func, '__name__') else 'unknown'}: {e}"
        )
        return error_value
    except Exception as e:
        logger.exception(
            f"Unexpected error in {func.__name__ if hasattr(func, '__name__') else 'unknown'}: {e}"
        )
        return error_value


async def get_aws_client_async(service_name: str, region: str = None):
    """Async wrapper for AWS client creation."""
    return get_aws_client(service_name, region)


class CloudFormationTroubleshooter:
    """Collects comprehensive CloudFormation troubleshooting data for LLM analysis."""
    
    def __init__(self, region: str = None, config=None):
        """Initialize the troubleshooter.
        
        Args:
            region: AWS region for operations (defaults to configured default)
            config: Optional configuration manager instance
        """
        self.config = config or config_manager
        self.region = region or self.config.get_config('aws.default_region')
        self.stack_manager = StackManager(self.region, self.config)
        self.cloudtrail_client = None  # Initialize lazily
        self.cfn_client = None  # Initialize lazily
        self.logs_client = None  # Initialize lazily
        
    async def _get_cloudtrail_client(self):
        """Get CloudTrail client, initializing if needed."""
        if self.cloudtrail_client is None:
            self.cloudtrail_client = await get_aws_client_async('cloudtrail', self.region)
        return self.cloudtrail_client
    
    async def _get_cfn_client(self):
        """Get CloudFormation client, initializing if needed."""
        if self.cfn_client is None:
            self.cfn_client = await get_aws_client_async('cloudformation', self.region)
        return self.cfn_client
    
    async def _get_logs_client(self):
        """Get CloudWatch Logs client, initializing if needed."""
        if self.logs_client is None:
            self.logs_client = await get_aws_client_async('logs', self.region)
        return self.logs_client
        
    async def analyze_stack(
        self,
        stack_name: str,
        include_logs: bool = True,
        include_cloudtrail: bool = True,
        time_window_hours: int = 24,
        symptoms_description: Optional[str] = None
    ) -> Dict[str, Any]:
        """Collect comprehensive CloudFormation stack data for LLM analysis."""
        try:
            analysis_start_time = datetime.utcnow()
            lookback_time = analysis_start_time - timedelta(hours=time_window_hours)
            
            # Initialize response structure (matching ECS MCP pattern)
            response = {
                'status': 'success',
                'stack_name': stack_name,
                'analysis_timestamp': analysis_start_time.isoformat(),
                'time_window_hours': time_window_hours,
                'assessment': '',
                'raw_data': {}
            }
            
            # Store symptoms description as raw input if provided
            if symptoms_description:
                response['raw_data']['symptoms_description'] = symptoms_description
            
            # 1. Discover and collect stack resources
            stack_resources = await self._discover_stack_resources(stack_name)
            response['raw_data']['discovered_resources'] = stack_resources
            
            # 2. Get comprehensive stack information
            stack_data = await self._collect_stack_data(stack_name)
            response['raw_data']['stack_info'] = stack_data
            
            # 3. Collect CloudTrail events for stack operations
            if include_cloudtrail:
                cloudtrail_data = await self._collect_cloudtrail_events(
                    stack_name, lookback_time, analysis_start_time
                )
                response['raw_data']['cloudtrail_events'] = cloudtrail_data
            
            # 4. Analyze failed resources in detail
            if stack_data.get('failed_resources'):
                resource_analysis = await self._analyze_failed_resources(
                    stack_data['failed_resources'], lookback_time
                )
                response['raw_data']['failed_resource_analysis'] = resource_analysis
            
            # 5. Collect CloudWatch logs
            if include_logs:
                logs_data = await self._collect_cloudwatch_logs(
                    stack_name, lookback_time, analysis_start_time
                )
                response['raw_data']['cloudwatch_logs'] = logs_data
            
            # 6. Collect dependency and configuration context
            context_data = await self._collect_context_data(stack_name, stack_data)
            response['raw_data']['context'] = context_data
            
            # 7. Create assessment (matching ECS MCP pattern)
            stack_status = stack_data.get('stack_status', 'UNKNOWN')
            response['assessment'] = self._create_assessment(stack_name, stack_status, stack_resources, stack_data)
            
            # 8. Create summary for LLM
            response['summary'] = self._create_analysis_summary(response['raw_data'])
            
            return response
            
        except Exception as e:
            logger.exception(f"Error in analyze_stack: {str(e)}")
            return {
                'status': 'error',
                'error': str(e),
                'stack_name': stack_name,
                'assessment': f'Error analyzing stack: {str(e)}',
                'analysis_timestamp': datetime.utcnow().isoformat()
            }
    
    async def _collect_stack_data(self, stack_name: str) -> Dict[str, Any]:
        """Collect comprehensive stack information."""
        try:
            stack_data = {
                'stack_exists': False,
                'stack_status': None,
                'stack_events': [],
                'stack_resources': [],
                'failed_resources': [],
                'stack_template': None,
                'stack_parameters': [],
                'stack_outputs': [],
                'stack_tags': [],
                'capabilities': [],
                'rollback_configuration': None
            }
            
            # Get CloudFormation client
            cfn_client = await self._get_cfn_client()
            
            # Get stack details
            try:
                stack_response = cfn_client.describe_stacks(StackName=stack_name)
                stack = stack_response['Stacks'][0]
                
                stack_data.update({
                    'stack_exists': True,
                    'stack_status': stack['StackStatus'],
                    'stack_id': stack['StackId'],
                    'creation_time': stack.get('CreationTime', '').isoformat() if stack.get('CreationTime') else None,
                    'last_updated_time': stack.get('LastUpdatedTime', '').isoformat() if stack.get('LastUpdatedTime') else None,
                    'stack_status_reason': stack.get('StackStatusReason'),
                    'stack_parameters': stack.get('Parameters', []),
                    'stack_outputs': stack.get('Outputs', []),
                    'stack_tags': stack.get('Tags', []),
                    'capabilities': stack.get('Capabilities', []),
                    'rollback_configuration': stack.get('RollbackConfiguration')
                })
                
            except ClientError as e:
                if 'does not exist' in str(e):
                    # Check for deleted stacks
                    deleted_stacks = await self._find_deleted_stacks(stack_name)
                    stack_data['deleted_stacks'] = deleted_stacks
                else:
                    stack_data['error'] = str(e)
                return stack_data
            
            # Get stack events
            try:
                events_response = cfn_client.describe_stack_events(StackName=stack_name)
                events = events_response['StackEvents']
                
                # Convert timestamps to ISO format and sort by timestamp
                for event in events:
                    if 'Timestamp' in event:
                        event['Timestamp'] = event['Timestamp'].isoformat()
                
                stack_data['stack_events'] = sorted(events, key=lambda x: x['Timestamp'], reverse=True)
                
                # Identify failed events
                failed_events = [
                    event for event in events 
                    if event['ResourceStatus'].endswith('_FAILED')
                ]
                stack_data['failed_events'] = failed_events
                
            except ClientError as e:
                stack_data['events_error'] = str(e)
            
            # Get stack resources
            try:
                resources_response = cfn_client.list_stack_resources(StackName=stack_name)
                resources = resources_response['StackResourceSummaries']
                
                # Convert timestamps
                for resource in resources:
                    if 'Timestamp' in resource:
                        resource['Timestamp'] = resource['Timestamp'].isoformat()
                
                stack_data['stack_resources'] = resources
                
                # Identify failed resources
                failed_resources = [
                    resource for resource in resources
                    if resource['ResourceStatus'].endswith('_FAILED')
                ]
                stack_data['failed_resources'] = failed_resources
                
            except ClientError as e:
                stack_data['resources_error'] = str(e)
            
            # Get stack template
            try:
                template_response = cfn_client.get_template(StackName=stack_name)
                stack_data['stack_template'] = template_response['TemplateBody']
            except ClientError as e:
                stack_data['template_error'] = str(e)
            
            return stack_data
            
        except Exception as e:
            logger.exception(f"Error collecting stack data for {stack_name}")
            return {'error': str(e), 'stack_exists': False}
    
    async def _collect_cloudtrail_events(
        self, 
        stack_name: str, 
        start_time: datetime, 
        end_time: datetime
    ) -> Dict[str, Any]:
        """Collect CloudTrail events related to the stack."""
        try:
            cloudtrail_data = {
                'events': [],
                'error_events': [],
                'api_call_summary': {
                    'total_calls': 0,
                    'failed_calls': 0,
                    'users': set(),
                    'source_ips': set(),
                    'event_types': {}
                }
            }
            
            # Get CloudTrail client
            cloudtrail_client = await self._get_cloudtrail_client()
            
            # Look up CloudTrail events for CloudFormation API calls
            try:
                cloudformation_events = [
                    'CreateStack', 'UpdateStack', 'DeleteStack', 'CancelUpdateStack',
                    'CreateChangeSet', 'ExecuteChangeSet', 'DeleteChangeSet',
                    'DescribeStacks', 'DescribeStackEvents', 'DescribeStackResources'
                ]
                
                for event_name in cloudformation_events:
                    events_response = await handle_aws_api_call(
                        cloudtrail_client.lookup_events,
                        {},
                        LookupAttributes=[
                            {
                                'AttributeKey': 'EventName',
                                'AttributeValue': event_name
                            }
                        ],
                        StartTime=start_time,
                        EndTime=end_time
                    )
                    
                    # Filter events related to our stack
                    for event in events_response.get('Events', []):
                        event_detail = json.loads(event.get('CloudTrailEvent', '{}'))
                        request_params = event_detail.get('requestParameters', {})
                        
                        # Check if this event is related to our stack
                        stack_related = (
                            request_params.get('stackName') == stack_name or
                            stack_name in str(event_detail) or
                            any(stack_name in str(param) for param in request_params.values() if isinstance(param, str))
                        )
                        
                        if stack_related:
                            # Convert timestamp
                            if 'EventTime' in event:
                                event['EventTime'] = event['EventTime'].isoformat()
                            
                            processed_event = {
                                'event_name': event.get('EventName'),
                                'event_time': event.get('EventTime'),
                                'username': event.get('Username'),
                                'user_identity': event_detail.get('userIdentity', {}),
                                'source_ip': event_detail.get('sourceIPAddress'),
                                'user_agent': event_detail.get('userAgent'),
                                'request_parameters': request_params,
                                'response_elements': event_detail.get('responseElements', {}),
                                'error_code': event_detail.get('errorCode'),
                                'error_message': event_detail.get('errorMessage'),
                                'aws_region': event_detail.get('awsRegion'),
                                'event_source': event_detail.get('eventSource')
                            }
                            
                            cloudtrail_data['events'].append(processed_event)
                            
                            # Update summary statistics
                            summary = cloudtrail_data['api_call_summary']
                            summary['total_calls'] += 1
                            summary['users'].add(processed_event.get('username', 'unknown'))
                            summary['source_ips'].add(processed_event.get('source_ip', 'unknown'))
                            
                            event_type = processed_event.get('event_name', 'unknown')
                            summary['event_types'][event_type] = summary['event_types'].get(event_type, 0) + 1
                            
                            # Separate error events
                            if processed_event.get('error_code') or processed_event.get('error_message'):
                                cloudtrail_data['error_events'].append(processed_event)
                                summary['failed_calls'] += 1
                
                # Convert sets to lists for JSON serialization
                summary = cloudtrail_data['api_call_summary']
                summary['users'] = list(summary['users'])
                summary['source_ips'] = list(summary['source_ips'])
                
            except Exception as e:
                cloudtrail_data['cloudtrail_error'] = str(e)
                logger.warning(f"Error collecting CloudTrail events: {e}")
            
            return cloudtrail_data
            
        except Exception as e:
            logger.exception(f"Error collecting CloudTrail events for {stack_name}")
            return {'error': str(e)}
    
    async def _analyze_failed_resources(
        self, 
        failed_resources: List[Dict], 
        lookback_time: datetime
    ) -> Dict[str, Any]:
        """Deep dive analysis of failed resources."""
        try:
            resource_analysis = {
                'detailed_analysis': []
            }
            
            for resource in failed_resources:
                resource_type = resource.get('ResourceType', '')
                logical_id = resource.get('LogicalResourceId', '')
                physical_id = resource.get('PhysicalResourceId', '')
                status_reason = resource.get('ResourceStatusReason', '')
                
                analysis = {
                    'logical_id': logical_id,
                    'physical_id': physical_id,
                    'resource_type': resource_type,
                    'status_reason': status_reason,
                    'service_specific_analysis': {}
                }
                
                # Analyze specific resource types
                if resource_type.startswith('AWS::IAM::'):
                    analysis['service_specific_analysis'] = await self._analyze_iam_resource(resource)
                elif resource_type.startswith('AWS::EC2::'):
                    analysis['service_specific_analysis'] = await self._analyze_ec2_resource(resource)
                elif resource_type.startswith('AWS::Lambda::'):
                    analysis['service_specific_analysis'] = await self._analyze_lambda_resource(resource)
                elif resource_type.startswith('AWS::S3::'):
                    analysis['service_specific_analysis'] = await self._analyze_s3_resource(resource)
                
                resource_analysis['detailed_analysis'].append(analysis)
            
            return resource_analysis
            
        except Exception as e:
            logger.exception("Error analyzing failed resources")
            return {'error': str(e)}
    
    async def _analyze_iam_resource(self, resource: Dict) -> Dict[str, Any]:
        """Analyze IAM resource failures."""
        try:
            analysis = {
                'resource_type': 'IAM',
                'common_issues': []
            }
            
            status_reason = resource.get('ResourceStatusReason', '')
            
            # Check for common IAM issues
            if 'already exists' in status_reason.lower():
                analysis['common_issues'].append('Resource name conflict - IAM resource already exists')
            
            if 'insufficient permissions' in status_reason.lower():
                analysis['common_issues'].append('Insufficient permissions to create IAM resource')
            
            if 'malformed policy' in status_reason.lower():
                analysis['common_issues'].append('Policy document syntax error')
            
            return analysis
            
        except Exception as e:
            return {'error': str(e)}
    
    async def _analyze_ec2_resource(self, resource: Dict) -> Dict[str, Any]:
        """Analyze EC2 resource failures."""
        try:
            analysis = {
                'resource_type': 'EC2',
                'common_issues': []
            }
            
            status_reason = resource.get('ResourceStatusReason', '')
            
            # Check for common EC2 issues
            if 'insufficient capacity' in status_reason.lower():
                analysis['common_issues'].append('Insufficient EC2 capacity in the requested AZ')
            
            if 'security group' in status_reason.lower():
                analysis['common_issues'].append('Security group configuration issue')
            
            if 'subnet' in status_reason.lower():
                analysis['common_issues'].append('Subnet configuration or availability issue')
            
            return analysis
            
        except Exception as e:
            return {'error': str(e)}
    
    async def _analyze_lambda_resource(self, resource: Dict) -> Dict[str, Any]:
        """Analyze Lambda resource failures."""
        try:
            analysis = {
                'resource_type': 'Lambda',
                'common_issues': []
            }
            
            status_reason = resource.get('ResourceStatusReason', '')
            
            # Check for common Lambda issues
            if 'code storage limit' in status_reason.lower():
                analysis['common_issues'].append('Lambda code storage limit exceeded')
            
            if 'invalid parameter' in status_reason.lower():
                analysis['common_issues'].append('Invalid Lambda function configuration parameter')
            
            return analysis
            
        except Exception as e:
            return {'error': str(e)}
    
    async def _analyze_s3_resource(self, resource: Dict) -> Dict[str, Any]:
        """Analyze S3 resource failures."""
        try:
            analysis = {
                'resource_type': 'S3',
                'common_issues': []
            }
            
            status_reason = resource.get('ResourceStatusReason', '')
            
            # Check for common S3 issues
            if 'already exists' in status_reason.lower():
                analysis['common_issues'].append('S3 bucket name already exists globally')
            
            if 'invalid bucket name' in status_reason.lower():
                analysis['common_issues'].append('S3 bucket name does not meet naming requirements')
            
            return analysis
            
        except Exception as e:
            return {'error': str(e)}
    
    async def _collect_cloudwatch_logs(
        self, 
        stack_name: str, 
        start_time: datetime, 
        end_time: datetime
    ) -> Dict[str, Any]:
        """Collect CloudWatch logs related to the stack."""
        try:
            logs_data = {
                'error_logs': []
            }
            
            # Get CloudWatch Logs client
            logs_client = await self._get_logs_client()
            
            # Look for log groups related to the stack
            try:
                log_groups_response = logs_client.describe_log_groups(
                    logGroupNamePrefix=f'/aws/lambda/{stack_name}'
                )
                
                for log_group in log_groups_response.get('logGroups', []):
                    log_group_name = log_group['logGroupName']
                    
                    # Get recent error logs
                    try:
                        start_time_ms = int(start_time.timestamp() * 1000)
                        end_time_ms = int(end_time.timestamp() * 1000)
                        
                        events_response = logs_client.filter_log_events(
                            logGroupName=log_group_name,
                            startTime=start_time_ms,
                            endTime=end_time_ms,
                            filterPattern='ERROR'
                        )
                        
                        for event in events_response.get('events', [])[:20]:  # Limit to 20 events
                            logs_data['error_logs'].append({
                                'timestamp': datetime.fromtimestamp(event['timestamp'] / 1000).isoformat(),
                                'message': event.get('message'),
                                'log_group': log_group_name
                            })
                            
                    except ClientError:
                        continue
                
            except ClientError as e:
                logs_data['logs_error'] = str(e)
            
            return logs_data
            
        except Exception as e:
            logger.exception(f"Error collecting CloudWatch logs for {stack_name}")
            return {'error': str(e)}
    
    async def _collect_context_data(self, stack_name: str, stack_data: Dict) -> Dict[str, Any]:
        """Collect contextual information about the stack and its environment."""
        try:
            context = {
                'template_analysis': {},
                'related_stacks': []
            }
            
            # Analyze template for dependencies and patterns
            if stack_data.get('stack_template'):
                template_str = stack_data['stack_template']
                try:
                    # Parse template string to dictionary
                    if isinstance(template_str, str):
                        try:
                            import yaml
                            template = yaml.safe_load(template_str)
                        except (ImportError, yaml.YAMLError):
                            try:
                                import json
                                template = json.loads(template_str)
                            except json.JSONDecodeError:
                                template = {}
                    else:
                        template = template_str
                    
                    if isinstance(template, dict):
                        context['template_analysis'] = {
                            'resource_count': len(template.get('Resources', {})),
                            'parameter_count': len(template.get('Parameters', {})),
                            'output_count': len(template.get('Outputs', {})),
                            'has_conditions': bool(template.get('Conditions')),
                            'has_mappings': bool(template.get('Mappings')),
                            'resource_types': list(set(
                                resource.get('Type', '') 
                                for resource in template.get('Resources', {}).values()
                            ))
                        }
                    else:
                        context['template_analysis'] = {
                            'error': 'Could not parse template as YAML or JSON'
                        }
                except Exception as e:
                    context['template_analysis'] = {
                        'error': f'Template parsing error: {str(e)}'
                    }
            
            # Look for related stacks (same prefix)
            try:
                cfn_client = await self._get_cfn_client()
                stacks_response = cfn_client.list_stacks(
                    StackStatusFilter=[
                        'CREATE_COMPLETE', 'UPDATE_COMPLETE', 'CREATE_FAILED', 
                        'UPDATE_FAILED', 'ROLLBACK_COMPLETE', 'ROLLBACK_FAILED'
                    ]
                )
                
                stack_prefix = stack_name.split('-')[0] if '-' in stack_name else stack_name[:5]
                related_stacks = [
                    {
                        'stack_name': stack['StackName'],
                        'stack_status': stack['StackStatus'],
                        'creation_time': stack.get('CreationTime', '').isoformat() if stack.get('CreationTime') else None
                    }
                    for stack in stacks_response['StackSummaries']
                    if stack['StackName'] != stack_name and stack_prefix in stack['StackName']
                ]
                
                context['related_stacks'] = related_stacks[:10]  # Limit to 10
                
            except ClientError as e:
                context['related_stacks_error'] = str(e)
            
            return context
            
        except Exception as e:
            logger.exception(f"Error collecting context data for {stack_name}")
            return {'error': str(e)}
    
    async def _find_deleted_stacks(self, stack_name: str) -> List[Dict]:
        """Find deleted stacks with the same name."""
        try:
            deleted_stacks = []
            cfn_client = await self._get_cfn_client()
            paginator = cfn_client.get_paginator('list_stacks')
            
            for page in paginator.paginate(StackStatusFilter=['DELETE_COMPLETE']):
                for stack_summary in page['StackSummaries']:
                    if stack_summary['StackName'] == stack_name:
                        deleted_stacks.append({
                            'stack_name': stack_summary['StackName'],
                            'stack_status': stack_summary['StackStatus'],
                            'deletion_time': stack_summary.get('DeletionTime', '').isoformat() if stack_summary.get('DeletionTime') else None,
                            'stack_id': stack_summary.get('StackId')
                        })
            
            return deleted_stacks
            
        except Exception as e:
            logger.exception(f"Error finding deleted stacks for {stack_name}")
            return []
    
    def _create_analysis_summary(self, raw_data: Dict) -> Dict[str, Any]:
        """Create a summary of the analysis for LLM consumption."""
        try:
            summary = {
                'stack_status': raw_data.get('stack_info', {}).get('stack_status'),
                'stack_exists': raw_data.get('stack_info', {}).get('stack_exists', False),
                'failed_resources_count': len(raw_data.get('stack_info', {}).get('failed_resources', [])),
                'error_events_count': len(raw_data.get('cloudtrail_events', {}).get('error_events', [])),
                'log_errors_count': len(raw_data.get('cloudwatch_logs', {}).get('error_logs', [])),
                'key_issues': [],
                'analysis_scope': {
                    'has_cloudtrail_data': bool(raw_data.get('cloudtrail_events', {}).get('events')),
                    'has_log_data': bool(raw_data.get('cloudwatch_logs', {}).get('error_logs')),
                    'has_failed_resources': bool(raw_data.get('failed_resource_analysis', {}).get('detailed_analysis')),
                    'template_analyzed': bool(raw_data.get('context', {}).get('template_analysis'))
                }
            }
            
            # Extract key issues from various sources
            stack_info = raw_data.get('stack_info', {})
            if stack_info.get('stack_status_reason'):
                summary['key_issues'].append({
                    'source': 'stack_status',
                    'issue': stack_info['stack_status_reason']
                })
            
            # Add failed resource issues
            for resource in stack_info.get('failed_resources', []):
                if resource.get('ResourceStatusReason'):
                    summary['key_issues'].append({
                        'source': 'failed_resource',
                        'resource': resource.get('LogicalResourceId'),
                        'issue': resource.get('ResourceStatusReason')
                    })
            
            return summary
            
        except Exception as e:
            logger.exception("Error creating analysis summary")
            return {'error': str(e)}
    
    async def recover_stack(
        self,
        stack_name: str,
        auto_fix: bool = False,
        backup_template: bool = True
    ) -> Dict[str, Any]:
        """Attempt to recover a failed CloudFormation stack."""
        try:
            recovery_result = {
                'success': True,
                'stack_name': stack_name,
                'recovery_timestamp': datetime.utcnow().isoformat(),
                'analysis': {},
                'recovery_options': [],
                'actions_taken': []
            }
            
            # First analyze the stack
            analysis = await self.analyze_stack(stack_name)
            recovery_result['analysis'] = analysis
            
            if not analysis['success']:
                return analysis
            
            # Backup template if requested
            if backup_template:
                backup_result = await self._backup_stack_template(stack_name)
                recovery_result['backup'] = backup_result
            
            # Provide recovery options based on stack state
            stack_status = analysis['raw_data']['stack_info']['stack_status']
            
            if stack_status in ['CREATE_FAILED', 'ROLLBACK_COMPLETE']:
                recovery_result['recovery_options'].extend([
                    'Delete the failed stack and recreate',
                    'Modify template to fix issues and retry',
                    'Continue rollback if stack is in UPDATE_ROLLBACK_FAILED state'
                ])
            
            elif stack_status in ['UPDATE_FAILED', 'UPDATE_ROLLBACK_FAILED']:
                recovery_result['recovery_options'].extend([
                    'Continue rollback to previous working state',
                    'Fix template issues and retry update',
                    'Cancel update and return to previous state'
                ])
            
            # If auto_fix is enabled, attempt basic recovery
            if auto_fix:
                cfn_client = await self._get_cfn_client()
                if stack_status == 'UPDATE_ROLLBACK_FAILED':
                    try:
                        cfn_client.continue_update_rollback(StackName=stack_name)
                        recovery_result['actions_taken'].append('Initiated continue update rollback')
                    except ClientError as e:
                        recovery_result['actions_taken'].append(f'Failed to continue rollback: {str(e)}')
            
            return recovery_result
            
        except Exception as e:
            logger.exception(f"Error recovering stack {stack_name}")
            return {
                'success': False,
                'error': str(e),
                'stack_name': stack_name
            }
    
    async def _backup_stack_template(self, stack_name: str) -> Dict[str, Any]:
        """Backup the current stack template."""
        try:
            cfn_client = await self._get_cfn_client()
            template_response = cfn_client.get_template(StackName=stack_name)
            template_body = json.dumps(template_response['TemplateBody'], indent=2)
            
            backup_filename = f"{stack_name}-backup-{int(time.time())}.json"
            
            with open(backup_filename, 'w') as f:
                f.write(template_body)
            
            return {
                'success': True,
                'backup_location': backup_filename,
                'backup_size': len(template_body)
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    async def _discover_stack_resources(self, stack_name: str) -> Dict[str, Any]:
        """Discover CloudFormation stack resources and related AWS resources."""
        try:
            resources = {
                'stacks': [],
                'related_stacks': [],
                'nested_stacks': [],
                'change_sets': [],
                'stack_sets': []
            }
            
            cfn_client = await get_aws_client_async('cloudformation', self.region)
            
            # Find the main stack
            try:
                stack_response = await handle_aws_api_call(
                    cfn_client.describe_stacks, 
                    {'Stacks': []}, 
                    StackName=stack_name
                )
                if stack_response and stack_response.get('Stacks'):
                    resources['stacks'] = [stack_response['Stacks'][0]['StackName']]
            except Exception:
                pass
            
            # Find related stacks (same prefix or containing stack name)
            try:
                all_stacks = await handle_aws_api_call(
                    cfn_client.list_stacks,
                    {'StackSummaries': []},
                    StackStatusFilter=[
                        'CREATE_COMPLETE', 'UPDATE_COMPLETE', 'CREATE_FAILED', 
                        'UPDATE_FAILED', 'ROLLBACK_COMPLETE', 'ROLLBACK_FAILED',
                        'DELETE_FAILED'
                    ]
                )
                
                if all_stacks and all_stacks.get('StackSummaries'):
                    stack_prefix = stack_name.split('-')[0] if '-' in stack_name else stack_name[:5]
                    for stack_summary in all_stacks['StackSummaries']:
                        stack_summary_name = stack_summary['StackName']
                        if (stack_summary_name != stack_name and 
                            (stack_prefix in stack_summary_name or stack_name in stack_summary_name)):
                            resources['related_stacks'].append(stack_summary_name)
            except Exception:
                pass
            
            # Find nested stacks
            try:
                nested_stacks = await handle_aws_api_call(
                    cfn_client.list_stacks,
                    {'StackSummaries': []},
                    StackStatusFilter=['CREATE_COMPLETE', 'UPDATE_COMPLETE', 'CREATE_FAILED', 'UPDATE_FAILED']
                )
                
                if nested_stacks and nested_stacks.get('StackSummaries'):
                    for stack_summary in nested_stacks['StackSummaries']:
                        # Check if this might be a nested stack by looking at the parent stack ID
                        if stack_summary.get('ParentId') and stack_name in str(stack_summary.get('ParentId', '')):
                            resources['nested_stacks'].append(stack_summary['StackName'])
            except Exception:
                pass
            
            # Find change sets
            try:
                change_sets = await handle_aws_api_call(
                    cfn_client.list_change_sets,
                    {'Summaries': []},
                    StackName=stack_name
                )
                
                if change_sets and change_sets.get('Summaries'):
                    resources['change_sets'] = [cs['ChangeSetName'] for cs in change_sets['Summaries']]
            except Exception:
                pass
            
            return resources
            
        except Exception as e:
            logger.exception(f"Error discovering stack resources for {stack_name}")
            return {'error': str(e)}
    
    async def _collect_stack_data(self, stack_name: str) -> Dict[str, Any]:
        """Collect comprehensive stack information with proper error handling."""
        try:
            stack_data = {
                'stack_exists': False,
                'stack_status': None,
                'stack_events': [],
                'stack_resources': [],
                'failed_resources': [],
                'stack_template': None,
                'stack_parameters': [],
                'stack_outputs': [],
                'stack_tags': [],
                'capabilities': [],
                'rollback_configuration': None
            }
            
            cfn_client = await get_aws_client_async('cloudformation', self.region)
            
            # Get stack details with error handling
            stack_response = await handle_aws_api_call(
                cfn_client.describe_stacks,
                None,
                StackName=stack_name
            )
            
            if not stack_response or not stack_response.get('Stacks'):
                # Check for deleted stacks
                deleted_stacks = await self._find_deleted_stacks(stack_name)
                stack_data['deleted_stacks'] = deleted_stacks
                return stack_data
            
            stack = stack_response['Stacks'][0]
            stack_data.update({
                'stack_exists': True,
                'stack_status': stack['StackStatus'],
                'stack_id': stack['StackId'],
                'creation_time': stack.get('CreationTime', '').isoformat() if stack.get('CreationTime') else None,
                'last_updated_time': stack.get('LastUpdatedTime', '').isoformat() if stack.get('LastUpdatedTime') else None,
                'stack_status_reason': stack.get('StackStatusReason'),
                'stack_parameters': stack.get('Parameters', []),
                'stack_outputs': stack.get('Outputs', []),
                'stack_tags': stack.get('Tags', []),
                'capabilities': stack.get('Capabilities', []),
                'rollback_configuration': stack.get('RollbackConfiguration')
            })
            
            # Get stack events with error handling
            events_response = await handle_aws_api_call(
                cfn_client.describe_stack_events,
                {'StackEvents': []},
                StackName=stack_name
            )
            
            if events_response and events_response.get('StackEvents'):
                events = events_response['StackEvents']
                
                # Convert timestamps to ISO format and sort by timestamp
                for event in events:
                    if 'Timestamp' in event:
                        event['Timestamp'] = event['Timestamp'].isoformat()
                
                stack_data['stack_events'] = sorted(events, key=lambda x: x['Timestamp'], reverse=True)
                
                # Identify failed events
                failed_events = [
                    event for event in events 
                    if event['ResourceStatus'].endswith('_FAILED')
                ]
                stack_data['failed_events'] = failed_events
            
            # Get stack resources with error handling
            resources_response = await handle_aws_api_call(
                cfn_client.list_stack_resources,
                {'StackResourceSummaries': []},
                StackName=stack_name
            )
            
            if resources_response and resources_response.get('StackResourceSummaries'):
                resources = resources_response['StackResourceSummaries']
                
                # Convert timestamps
                for resource in resources:
                    if 'Timestamp' in resource:
                        resource['Timestamp'] = resource['Timestamp'].isoformat()
                
                stack_data['stack_resources'] = resources
                
                # Identify failed resources
                failed_resources = [
                    resource for resource in resources
                    if resource['ResourceStatus'].endswith('_FAILED')
                ]
                stack_data['failed_resources'] = failed_resources
            
            # Get stack template with error handling
            template_response = await handle_aws_api_call(
                cfn_client.get_template,
                None,
                StackName=stack_name
            )
            
            if template_response and template_response.get('TemplateBody'):
                stack_data['stack_template'] = template_response['TemplateBody']
            
            return stack_data
            
        except Exception as e:
            logger.exception(f"Error collecting stack data for {stack_name}")
            return {'error': str(e), 'stack_exists': False}
    
    def _create_assessment(self, stack_name: str, stack_status: str, resources: Dict, stack_data: Dict) -> str:
        """Create a human-readable assessment of the stack's state (matching ECS MCP pattern)."""
        
        if stack_status == "UNKNOWN" or not stack_data.get('stack_exists'):
            assessment = (
                f"CloudFormation stack '{stack_name}' does not exist or could not be accessed. "
                f"Stack deployment may have failed or not been attempted."
            )
            
            # Add information about deleted stacks if found
            if stack_data.get('deleted_stacks'):
                assessment += f" Found {len(stack_data['deleted_stacks'])} previously deleted stacks with the same name."
            
            # Add information about related resources if found
            if resources.get('related_stacks'):
                assessment += f" Found {len(resources['related_stacks'])} related stacks that may be relevant."
        
        elif "ROLLBACK" in stack_status or "FAILED" in stack_status:
            assessment = (
                f"CloudFormation stack '{stack_name}' exists but is in a failed state: {stack_status}."
            )
            
            # Add failure details
            failed_resources_count = len(stack_data.get('failed_resources', []))
            if failed_resources_count > 0:
                assessment += f" {failed_resources_count} resources failed during deployment."
            
            if stack_data.get('stack_status_reason'):
                assessment += f" Reason: {stack_data['stack_status_reason']}"
        
        elif "IN_PROGRESS" in stack_status:
            assessment = (
                f"CloudFormation stack '{stack_name}' is currently being processed: {stack_status}. "
                f"Operation may still be in progress."
            )
        
        elif stack_status in ["CREATE_COMPLETE", "UPDATE_COMPLETE"]:
            assessment = (
                f"CloudFormation stack '{stack_name}' exists and is in a successful state: {stack_status}."
            )
            
            # Check for any resources that might have issues
            resource_count = len(stack_data.get('stack_resources', []))
            if resource_count > 0:
                assessment += f" Stack contains {resource_count} resources."
            
            # Check for nested stacks
            if resources.get('nested_stacks'):
                assessment += f" Stack has {len(resources['nested_stacks'])} nested stacks."
        
        elif stack_status == "DELETE_COMPLETE":
            assessment = (
                f"CloudFormation stack '{stack_name}' has been successfully deleted."
            )
        
        elif "DELETE" in stack_status:
            assessment = (
                f"CloudFormation stack '{stack_name}' is in deletion state: {stack_status}."
            )
        
        else:
            assessment = f"CloudFormation stack '{stack_name}' is in status: {stack_status}."
        
        # Add context about related resources
        if resources.get('change_sets'):
            assessment += f" Stack has {len(resources['change_sets'])} change sets available."
        
        return assessment
    
