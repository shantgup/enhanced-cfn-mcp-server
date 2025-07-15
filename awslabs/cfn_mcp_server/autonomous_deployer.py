"""
Autonomous CloudFormation Deployment Engine

This module provides autonomous deployment capabilities that can iteratively
fix and deploy CloudFormation stacks until successful deployment.
"""

import json
import time
import boto3
from typing import Dict, List, Any, Optional, Tuple
try:
    import yaml
except ImportError:
    yaml = None
from dataclasses import dataclass
import logging

from .template_analyzer import TemplateAnalyzer
from .template_fixer import TemplateFixer

logger = logging.getLogger(__name__)

@dataclass
class DeploymentAttempt:
    """Represents a deployment attempt"""
    attempt_number: int
    template: Dict[str, Any]
    stack_id: Optional[str]
    status: str
    error_message: Optional[str]
    fixes_applied: List[Any]
    timestamp: float

class AutonomousDeployer:
    """Autonomous CloudFormation deployment with iterative fixing"""
    
    def __init__(self, region: str = 'us-east-1'):
        self.region = region
        self.cfn_client = boto3.client('cloudformation', region_name=region)
        self.analyzer = TemplateAnalyzer()
        self.fixer = TemplateFixer()
        self.deployment_history = []
    
    def deploy_with_auto_fix(self, stack_name: str, template: Dict[str, Any], 
                           parameters: Optional[List[Dict]] = None,
                           capabilities: Optional[List[str]] = None,
                           tags: Optional[List[Dict]] = None,
                           max_iterations: int = 5,
                           wait_timeout: int = 1800) -> Dict[str, Any]:
        """
        Deploy stack with automatic fixing and retry
        
        Args:
            stack_name: CloudFormation stack name
            template: CloudFormation template
            parameters: Stack parameters
            capabilities: IAM capabilities
            tags: Stack tags
            max_iterations: Maximum fix-deploy iterations
            wait_timeout: Timeout for each deployment attempt
            
        Returns:
            Deployment result with success status and details
        """
        try:
            result = {
                'success': False,
                'final_stack_status': None,
                'deployment_attempts': [],
                'total_fixes_applied': [],
                'final_template': template,
                'error_message': None
            }
            
            current_template = template.copy()
            
            for iteration in range(max_iterations):
                logger.info(f"Starting deployment iteration {iteration + 1}/{max_iterations}")
                
                # Analyze template before deployment
                analysis = self.analyzer.analyze_template(current_template)
                
                # Apply fixes if issues found
                if analysis.get('issues') or analysis.get('security_issues'):
                    logger.info(f"Found {len(analysis.get('issues', []))} issues, applying fixes...")
                    
                    fix_result = self.fixer.fix_template(
                        current_template, 
                        analysis, 
                        auto_apply=True
                    )
                    
                    if fix_result['success']:
                        current_template = fix_result['fixed_template']
                        result['total_fixes_applied'].extend(fix_result['fixes_applied'])
                        logger.info(f"Applied {len(fix_result['fixes_applied'])} fixes")
                    else:
                        logger.warning(f"Failed to apply fixes: {fix_result.get('error')}")
                
                # Attempt deployment
                deployment_result = self._deploy_stack(
                    stack_name=stack_name,
                    template=current_template,
                    parameters=parameters,
                    capabilities=capabilities,
                    tags=tags,
                    wait_timeout=wait_timeout
                )
                
                attempt = DeploymentAttempt(
                    attempt_number=iteration + 1,
                    template=current_template.copy(),
                    stack_id=deployment_result.get('stack_id'),
                    status=deployment_result['status'],
                    error_message=deployment_result.get('error_message'),
                    fixes_applied=fix_result.get('fixes_applied', []) if 'fix_result' in locals() else [],
                    timestamp=time.time()
                )
                
                result['deployment_attempts'].append(attempt)
                
                if deployment_result['success']:
                    result['success'] = True
                    result['final_stack_status'] = deployment_result['status']
                    result['final_template'] = current_template
                    logger.info(f"Deployment successful after {iteration + 1} iterations")
                    break
                else:
                    logger.warning(f"Deployment attempt {iteration + 1} failed: {deployment_result.get('error_message')}")
                    
                    # Analyze failure and apply targeted fixes
                    if deployment_result.get('stack_events'):
                        failure_fixes = self._analyze_and_fix_deployment_failure(
                            current_template,
                            deployment_result['stack_events']
                        )
                        
                        if failure_fixes['fixes_applied']:
                            current_template = failure_fixes['fixed_template']
                            result['total_fixes_applied'].extend(failure_fixes['fixes_applied'])
                            logger.info(f"Applied {len(failure_fixes['fixes_applied'])} failure-specific fixes")
                        else:
                            logger.warning("No failure-specific fixes could be applied")
                            if iteration == max_iterations - 1:
                                result['error_message'] = deployment_result.get('error_message')
                                break
            
            if not result['success']:
                result['error_message'] = f"Failed to deploy after {max_iterations} iterations"
                logger.error(result['error_message'])
            
            return result
            
        except Exception as e:
            logger.exception(f"Error in autonomous deployment: {e}")
            return {
                'success': False,
                'error_message': str(e),
                'deployment_attempts': [],
                'total_fixes_applied': []
            }
    
    def _deploy_stack(self, stack_name: str, template: Dict[str, Any],
                     parameters: Optional[List[Dict]] = None,
                     capabilities: Optional[List[str]] = None,
                     tags: Optional[List[Dict]] = None,
                     wait_timeout: int = 1800) -> Dict[str, Any]:
        """Deploy CloudFormation stack"""
        try:
            # Convert template to JSON string
            template_body = json.dumps(template, indent=2)
            
            # Prepare deployment parameters
            deploy_params = {
                'StackName': stack_name,
                'TemplateBody': template_body
            }
            
            if parameters:
                deploy_params['Parameters'] = parameters
            if capabilities:
                deploy_params['Capabilities'] = capabilities
            if tags:
                deploy_params['Tags'] = tags
            
            # Check if stack exists
            stack_exists = self._stack_exists(stack_name)
            
            if stack_exists:
                logger.info(f"Updating existing stack: {stack_name}")
                response = self.cfn_client.update_stack(**deploy_params)
                operation = 'UPDATE'
            else:
                logger.info(f"Creating new stack: {stack_name}")
                response = self.cfn_client.create_stack(**deploy_params)
                operation = 'CREATE'
            
            stack_id = response['StackId']
            
            # Wait for deployment to complete
            wait_result = self._wait_for_stack_operation(stack_name, operation, wait_timeout)
            
            return {
                'success': wait_result['success'],
                'stack_id': stack_id,
                'status': wait_result['final_status'],
                'error_message': wait_result.get('error_message'),
                'stack_events': wait_result.get('stack_events', [])
            }
            
        except self.cfn_client.exceptions.ValidationError as e:
            logger.error(f"Template validation error: {e}")
            return {
                'success': False,
                'error_message': str(e),
                'stack_events': []
            }
        except Exception as e:
            logger.exception(f"Error deploying stack: {e}")
            return {
                'success': False,
                'error_message': str(e),
                'stack_events': []
            }
    
    def _wait_for_stack_operation(self, stack_name: str, operation: str, 
                                 timeout: int = 1800) -> Dict[str, Any]:
        """Wait for stack operation to complete"""
        try:
            if operation == 'CREATE':
                waiter = self.cfn_client.get_waiter('stack_create_complete')
                success_statuses = ['CREATE_COMPLETE']
                failure_statuses = ['CREATE_FAILED', 'ROLLBACK_COMPLETE', 'ROLLBACK_FAILED']
            else:  # UPDATE
                waiter = self.cfn_client.get_waiter('stack_update_complete')
                success_statuses = ['UPDATE_COMPLETE']
                failure_statuses = ['UPDATE_FAILED', 'UPDATE_ROLLBACK_COMPLETE', 'UPDATE_ROLLBACK_FAILED']
            
            start_time = time.time()
            
            try:
                waiter.wait(
                    StackName=stack_name,
                    WaiterConfig={
                        'Delay': 30,
                        'MaxAttempts': timeout // 30
                    }
                )
                
                # Get final stack status
                stack_info = self.cfn_client.describe_stacks(StackName=stack_name)
                final_status = stack_info['Stacks'][0]['StackStatus']
                
                return {
                    'success': final_status in success_statuses,
                    'final_status': final_status,
                    'duration': time.time() - start_time
                }
                
            except self.cfn_client.exceptions.WaiterError:
                # Get stack events for failure analysis
                stack_events = self._get_stack_events(stack_name)
                stack_info = self.cfn_client.describe_stacks(StackName=stack_name)
                final_status = stack_info['Stacks'][0]['StackStatus']
                
                return {
                    'success': False,
                    'final_status': final_status,
                    'duration': time.time() - start_time,
                    'stack_events': stack_events,
                    'error_message': f'Stack operation failed with status: {final_status}'
                }
                
        except Exception as e:
            logger.exception(f"Error waiting for stack operation: {e}")
            return {
                'success': False,
                'error_message': str(e),
                'stack_events': []
            }
    
    def _get_stack_events(self, stack_name: str, max_events: int = 100) -> List[Dict[str, Any]]:
        """Get CloudFormation stack events"""
        try:
            paginator = self.cfn_client.get_paginator('describe_stack_events')
            events = []
            
            for page in paginator.paginate(StackName=stack_name):
                events.extend(page['StackEvents'])
                if len(events) >= max_events:
                    break
            
            # Sort by timestamp (newest first)
            events.sort(key=lambda x: x['Timestamp'], reverse=True)
            
            return events[:max_events]
            
        except Exception as e:
            logger.exception(f"Error getting stack events: {e}")
            return []
    
    def _analyze_and_fix_deployment_failure(self, template: Dict[str, Any], 
                                          stack_events: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze deployment failure and apply targeted fixes"""
        try:
            result = {
                'fixed_template': template.copy(),
                'fixes_applied': [],
                'analysis': {}
            }
            
            # Find failed events
            failed_events = [
                event for event in stack_events
                if event.get('ResourceStatus', '').endswith('_FAILED')
            ]
            
            if not failed_events:
                return result
            
            # Analyze each failure
            for event in failed_events:
                resource_id = event.get('LogicalResourceId')
                status_reason = event.get('ResourceStatusReason', '')
                
                logger.info(f"Analyzing failure for {resource_id}: {status_reason}")
                
                # Apply targeted fix for this specific failure
                fix_result = self.fixer.fix_specific_failure(
                    result['fixed_template'],
                    status_reason,
                    resource_id
                )
                
                if fix_result['success']:
                    result['fixed_template'] = fix_result['fixed_template']
                    result['fixes_applied'].extend(fix_result['fixes_applied'])
                    logger.info(f"Applied fix for {resource_id}")
                else:
                    logger.warning(f"Could not fix failure for {resource_id}: {fix_result.get('error')}")
            
            return result
            
        except Exception as e:
            logger.exception(f"Error analyzing deployment failure: {e}")
            return {
                'fixed_template': template,
                'fixes_applied': [],
                'analysis': {'error': str(e)}
            }
    
    def _stack_exists(self, stack_name: str) -> bool:
        """Check if CloudFormation stack exists"""
        try:
            self.cfn_client.describe_stacks(StackName=stack_name)
            return True
        except self.cfn_client.exceptions.ClientError as e:
            if 'does not exist' in str(e):
                return False
            raise
    
    def validate_template_before_deployment(self, template: Dict[str, Any]) -> Dict[str, Any]:
        """Validate template before deployment"""
        try:
            # CloudFormation validation
            template_body = json.dumps(template, indent=2)
            validation_result = self.cfn_client.validate_template(TemplateBody=template_body)
            
            # Our own analysis
            analysis = self.analyzer.analyze_template(template)
            
            return {
                'valid': True,
                'cfn_validation': validation_result,
                'analysis': analysis,
                'recommendations': analysis.get('recommendations', [])
            }
            
        except Exception as e:
            logger.exception(f"Error validating template: {e}")
            return {
                'valid': False,
                'error': str(e),
                'analysis': {}
            }
    
    def get_deployment_summary(self) -> Dict[str, Any]:
        """Get summary of all deployment attempts"""
        if not self.deployment_history:
            return {'message': 'No deployments attempted'}
        
        total_attempts = len(self.deployment_history)
        successful_deployments = sum(1 for attempt in self.deployment_history if attempt.status == 'SUCCESS')
        
        return {
            'total_attempts': total_attempts,
            'successful_deployments': successful_deployments,
            'success_rate': successful_deployments / total_attempts if total_attempts > 0 else 0,
            'recent_attempts': self.deployment_history[-5:] if len(self.deployment_history) > 5 else self.deployment_history
        }
    
    def rollback_stack(self, stack_name: str) -> Dict[str, Any]:
        """Rollback CloudFormation stack to previous version"""
        try:
            logger.info(f"Rolling back stack: {stack_name}")
            
            # Cancel any in-progress update
            try:
                self.cfn_client.cancel_update_stack(StackName=stack_name)
                time.sleep(30)  # Wait for cancellation
            except Exception:
                pass  # Stack might not be in update state
            
            # Initiate rollback
            self.cfn_client.continue_update_rollback(StackName=stack_name)
            
            # Wait for rollback to complete
            waiter = self.cfn_client.get_waiter('stack_update_complete')
            waiter.wait(StackName=stack_name)
            
            return {
                'success': True,
                'message': f'Stack {stack_name} rolled back successfully'
            }
            
        except Exception as e:
            logger.exception(f"Error rolling back stack: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def cleanup_failed_stack(self, stack_name: str) -> Dict[str, Any]:
        """Clean up failed stack deployment"""
        try:
            logger.info(f"Cleaning up failed stack: {stack_name}")
            
            # Get stack status
            stack_info = self.cfn_client.describe_stacks(StackName=stack_name)
            stack_status = stack_info['Stacks'][0]['StackStatus']
            
            if stack_status in ['CREATE_FAILED', 'ROLLBACK_COMPLETE']:
                # Delete the failed stack
                self.cfn_client.delete_stack(StackName=stack_name)
                
                # Wait for deletion
                waiter = self.cfn_client.get_waiter('stack_delete_complete')
                waiter.wait(StackName=stack_name)
                
                return {
                    'success': True,
                    'message': f'Failed stack {stack_name} deleted successfully'
                }
            else:
                return {
                    'success': False,
                    'message': f'Stack {stack_name} is in status {stack_status}, cannot clean up'
                }
                
        except Exception as e:
            logger.exception(f"Error cleaning up failed stack: {e}")
            return {
                'success': False,
                'error': str(e)
            }
