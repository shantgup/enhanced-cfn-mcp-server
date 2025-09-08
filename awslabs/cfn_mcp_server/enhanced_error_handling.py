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

"""Enhanced error handling for CloudFormation operations."""

from typing import Dict, List, Any, Optional
import re
import traceback


def enhanced_error_handling(error: Exception, operation: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Provide enhanced error handling with context-aware suggestions.
    
    Args:
        error: The exception that was raised
        operation: The operation that was being performed
        context: Optional context information (resource type, etc.)
        
    Returns:
        Dictionary with error details and suggestions
    """
    error_message = str(error)
    error_type = type(error).__name__
    
    # Default response
    response = {
        'success': False,
        'error': error_message,
        'error_type': error_type,
        'operation': operation,
        'suggestions': [],
        'documentation_links': [],
        'user_friendly_message': _get_user_friendly_message(error_message, operation),
        'traceback': _get_formatted_traceback()
    }
    
    # Add context if provided
    if context:
        response['context'] = context
    
    # Add operation-specific suggestions
    if operation == 'get_resource_schema_information':
        response['suggestions'] = [
            'Verify that the resource type is valid and supported by CloudFormation',
            'Check AWS credentials and permissions',
            'Ensure the region specified is valid and available'
        ]
        response['documentation_links'] = [
            'https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-template-resource-type-ref.html'
        ]
    
    elif operation == 'generate_cloudformation_template':
        response['suggestions'] = [
            'Try providing more specific details in your description',
            'Check for syntax errors in your input',
            'Specify the region explicitly if targeting a specific region'
        ]
    
    elif operation == 'deploy_cloudformation_stack':
        response['suggestions'] = _get_deployment_error_suggestions(error_message)
        response['documentation_links'] = [
            'https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/troubleshooting.html'
        ]
    
    elif operation == 'enhanced_troubleshoot_cloudformation_stack':
        response['suggestions'] = [
            'Verify the stack name is correct',
            'Ensure you have permissions to view stack resources',
            'Check if the stack exists in the specified region'
        ]
    
    # Add error-specific suggestions
    error_specific_suggestions = _get_error_specific_suggestions(error_message)
    if error_specific_suggestions:
        response['suggestions'].extend(error_specific_suggestions)
    
    # Add recovery steps if applicable
    recovery_steps = _get_recovery_steps(error_message, operation)
    if recovery_steps:
        response['recovery_steps'] = recovery_steps
    
    return response


def _get_deployment_error_suggestions(error_message: str) -> List[str]:
    """Get suggestions for deployment errors."""
    suggestions = [
        'Validate your template before deployment',
        'Check that you have the necessary permissions'
    ]
    
    if 'No updates are to be performed' in error_message:
        suggestions.append('The stack is already up to date, no changes needed')
    
    elif 'Template format error' in error_message:
        suggestions.append('Check your template for syntax errors')
        suggestions.append('Ensure your template is valid YAML or JSON')
    
    elif 'Requires capabilities' in error_message:
        if 'CAPABILITY_IAM' in error_message:
            suggestions.append('Add CAPABILITY_IAM to your deployment request')
        if 'CAPABILITY_NAMED_IAM' in error_message:
            suggestions.append('Add CAPABILITY_NAMED_IAM to your deployment request')
        if 'CAPABILITY_AUTO_EXPAND' in error_message:
            suggestions.append('Add CAPABILITY_AUTO_EXPAND to your deployment request')
    
    elif 'Parameter' in error_message and 'cannot be used' in error_message:
        suggestions.append('Check that all parameters in your request match the template parameters')
    
    elif 'Rate exceeded' in error_message:
        suggestions.append('You are being throttled, try again with exponential backoff')
    
    return suggestions


def _get_error_specific_suggestions(error_message: str) -> List[str]:
    """Get suggestions based on specific error messages."""
    suggestions = []
    
    if 'AccessDenied' in error_message:
        suggestions.append('Check your IAM permissions')
        suggestions.append('Verify that your credentials are valid')
    
    elif 'ValidationError' in error_message:
        suggestions.append('Check your input parameters for errors')
        suggestions.append('Ensure your template follows CloudFormation syntax')
    
    elif 'ResourceNotFoundException' in error_message:
        suggestions.append('Verify that the resource exists in the specified region')
        suggestions.append('Check for typos in resource identifiers')
    
    elif 'LimitExceededException' in error_message:
        suggestions.append('You have reached a service limit, request a limit increase')
        suggestions.append('Try deleting unused resources')
    
    elif 'ThrottlingException' in error_message:
        suggestions.append('Implement exponential backoff in your requests')
        suggestions.append('Reduce the frequency of your API calls')
    
    return suggestions


def _get_recovery_steps(error_message: str, operation: str) -> List[str]:
    """Get recovery steps based on the error and operation."""
    recovery_steps = []
    
    if operation == 'deploy_cloudformation_stack':
        if 'CREATE_FAILED' in error_message:
            recovery_steps = [
                {
                    'step': 'Delete the failed stack',
                    'description': 'Remove the failed stack to clean up resources',
                    'aws_cli_command': 'aws cloudformation delete-stack --stack-name <stack-name>'
                },
                {
                    'step': 'Fix the issues in your template',
                    'description': 'Address the errors identified in the stack events',
                    'aws_cli_command': 'aws cloudformation validate-template --template-body file://template.yaml'
                },
                {
                    'step': 'Deploy the stack again with the fixed template',
                    'description': 'Create a new stack with the corrected template',
                    'aws_cli_command': 'aws cloudformation create-stack --stack-name <stack-name> --template-body file://template.yaml --capabilities CAPABILITY_IAM'
                }
            ]
        elif 'UPDATE_FAILED' in error_message:
            recovery_steps = [
                {
                    'step': 'Check if the stack is in UPDATE_ROLLBACK_FAILED state',
                    'description': 'Verify the current stack status',
                    'aws_cli_command': 'aws cloudformation describe-stacks --stack-name <stack-name>'
                },
                {
                    'step': 'Continue update rollback if needed',
                    'description': 'If the stack is in UPDATE_ROLLBACK_FAILED state, continue the rollback',
                    'aws_cli_command': 'aws cloudformation continue-update-rollback --stack-name <stack-name>'
                },
                {
                    'step': 'Fix the issues in your template',
                    'description': 'Address the errors identified in the stack events',
                    'aws_cli_command': 'aws cloudformation validate-template --template-body file://template.yaml'
                },
                {
                    'step': 'Update the stack again with the fixed template',
                    'description': 'Apply the corrected template to the stack',
                    'aws_cli_command': 'aws cloudformation update-stack --stack-name <stack-name> --template-body file://template.yaml --capabilities CAPABILITY_IAM'
                }
            ]
    
    elif operation == 'delete_cloudformation_stack':
        if 'DELETE_FAILED' in error_message:
            recovery_steps = [
                {
                    'step': 'Identify resources preventing deletion',
                    'description': 'Check stack events to find resources that failed to delete',
                    'aws_cli_command': 'aws cloudformation describe-stack-events --stack-name <stack-name>'
                },
                {
                    'step': 'Check for resources with deletion protection',
                    'description': 'Some resources like RDS instances may have deletion protection enabled',
                    'aws_cli_command': 'aws rds describe-db-instances --query "DBInstances[?DBInstanceIdentifier.contains(@, \'<stack-name>\')].DeletionProtection"'
                },
                {
                    'step': 'Disable deletion protection on resources',
                    'description': 'Update resources to disable deletion protection',
                    'aws_cli_command': 'aws rds modify-db-instance --db-instance-identifier <db-instance-id> --no-deletion-protection'
                },
                {
                    'step': 'Retry deletion with RetainResources for problematic resources',
                    'description': 'Delete the stack but retain specific resources that can be cleaned up manually',
                    'aws_cli_command': 'aws cloudformation delete-stack --stack-name <stack-name> --retain-resources "Resource1" "Resource2"'
                }
            ]
    
    elif operation == 'enhanced_troubleshoot_cloudformation_stack':
        recovery_steps = [
            {
                'step': 'Check stack status',
                'description': 'Verify the current state of the stack',
                'aws_cli_command': 'aws cloudformation describe-stacks --stack-name <stack-name>'
            },
            {
                'step': 'Review stack events',
                'description': 'Examine stack events to identify failures',
                'aws_cli_command': 'aws cloudformation describe-stack-events --stack-name <stack-name>'
            },
            {
                'step': 'Check resource status',
                'description': 'Verify the status of stack resources',
                'aws_cli_command': 'aws cloudformation describe-stack-resources --stack-name <stack-name>'
            },
            {
                'step': 'Validate template',
                'description': 'Check template for syntax errors',
                'aws_cli_command': 'aws cloudformation validate-template --template-body file://template.yaml'
            }
        ]
    
    return recovery_steps


def _get_user_friendly_message(error_message: str, operation: str) -> str:
    """Get a user-friendly error message.
    
    Args:
        error_message: The original error message
        operation: The operation being performed
        
    Returns:
        A user-friendly error message
    """
    # Stack state errors
    if 'is in CREATE_IN_PROGRESS state' in error_message:
        return "The stack is currently being created. Please wait for the creation to complete before performing this operation."
    
    if 'is in UPDATE_IN_PROGRESS state' in error_message:
        return "The stack is currently being updated. Please wait for the update to complete before performing this operation."
    
    if 'is in DELETE_IN_PROGRESS state' in error_message:
        return "The stack is currently being deleted. Please wait for the deletion to complete before performing this operation."
    
    if 'Drift detection' in error_message and 'can only be performed on stacks' in error_message:
        return "Drift detection can only be performed on stacks in stable states (CREATE_COMPLETE, UPDATE_COMPLETE, or UPDATE_ROLLBACK_COMPLETE). Please wait for the current operation to complete."
    
    # Capability errors
    if 'Requires capabilities' in error_message:
        capabilities = []
        if 'CAPABILITY_IAM' in error_message:
            capabilities.append('CAPABILITY_IAM')
        if 'CAPABILITY_NAMED_IAM' in error_message:
            capabilities.append('CAPABILITY_NAMED_IAM')
        if 'CAPABILITY_AUTO_EXPAND' in error_message:
            capabilities.append('CAPABILITY_AUTO_EXPAND')
        
        capability_str = ', '.join(capabilities)
        return f"This template requires additional capabilities: {capability_str}. These are required because the template creates IAM resources or uses transforms."
    
    # No updates error
    if 'No updates are to be performed' in error_message:
        return "The stack is already up to date. No changes were detected between the current stack and the template you provided."
    
    # Validation errors
    if 'Template format error' in error_message:
        return "The template contains syntax errors. Please check the template format and try again."
    
    # Resource errors
    if 'Resource does not exist' in error_message:
        return "The requested resource could not be found. Please check that the resource identifier is correct and that you have permission to access it."
    
    # Default message
    if operation == 'get_resource_schema_information':
        return "Failed to retrieve resource schema information. Please check that the resource type is valid and supported by CloudFormation."
    
    if operation == 'generate_cloudformation_template':
        return "Failed to generate CloudFormation template. Please check your input and try again with more specific details."
    
    if operation == 'deploy_cloudformation_stack':
        return "Failed to deploy CloudFormation stack. Please check the template for errors and ensure you have the necessary permissions."
    
    if operation == 'enhanced_troubleshoot_cloudformation_stack':
        return "Failed to troubleshoot CloudFormation stack. Please check that the stack exists and that you have permission to access it."
    
    # Generic message
    return f"An error occurred while performing the {operation} operation. Please check the error details for more information."


def _get_formatted_traceback() -> str:
    """Get a formatted traceback of the current exception.
    
    Returns:
        Formatted traceback as string
    """
    return traceback.format_exc()