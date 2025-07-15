"""User-friendly error messages for CloudFormation operations."""

from typing import Dict, Any, Optional


def get_user_friendly_error(error: Exception, operation: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Get a user-friendly error message with actionable suggestions.
    
    Args:
        error: The exception that was raised
        operation: The operation being performed
        context: Additional context information
        
    Returns:
        Dictionary with user-friendly error message and suggestions
    """
    error_message = str(error)
    error_type = type(error).__name__
    
    # Default response
    response = {
        'success': False,
        'error': error_message,
        'error_type': error_type,
        'operation': operation,
        'user_friendly_message': _get_user_friendly_message(error_message, operation),
        'suggestions': _get_error_suggestions(error_message, operation)
    }
    
    # Add context if provided
    if context:
        response['context'] = context
    
    return response


def _get_user_friendly_message(error_message: str, operation: str) -> str:
    """Get a user-friendly error message.
    
    Args:
        error_message: The original error message
        operation: The operation being performed
        
    Returns:
        A user-friendly error message
    """
    # Template generation errors
    if operation == 'generate_cloudformation_template':
        if 'invalid group reference' in error_message:
            return "There was an issue with the template generation process. We're working to fix this."
        
        if 'KeyError' in error_message:
            return "The template generator couldn't find a required resource or property."
        
        if 'AttributeError' in error_message:
            return "The template generator encountered an issue with a resource attribute."
        
        return "There was an issue generating the CloudFormation template. Please try with a more specific description."
    
    # Template validation errors
    if operation == 'validate_template':
        if 'Template format error' in error_message:
            return "The template contains syntax errors. Please check the template format."
        
        if 'No updates are to be performed' in error_message:
            return "The stack is already up to date. No changes were detected."
        
        if 'Requires capabilities' in error_message:
            return "This template requires additional capabilities to create IAM resources or use transforms."
        
        return "Template validation failed. Please check the template for errors."
    
    # Stack deployment errors
    if operation == 'deploy_simple_stack':
        if 'AlreadyExistsException' in error_message:
            return "A stack with this name already exists. Please use a different name or update the existing stack."
        
        if 'ValidationError' in error_message and 'No updates are to be performed' in error_message:
            return "The stack is already up to date. No changes were detected."
        
        if 'ValidationError' in error_message and 'Template error' in error_message:
            return "The template contains errors that prevent deployment. Please fix the template and try again."
        
        return "Failed to deploy the CloudFormation stack. Please check the error details."
    
    # Generic message
    return f"An error occurred while performing the {operation} operation. Please check the error details."


def _get_error_suggestions(error_message: str, operation: str) -> list:
    """Get suggestions for resolving the error.
    
    Args:
        error_message: The original error message
        operation: The operation being performed
        
    Returns:
        List of suggestions
    """
    # Template generation errors
    if operation == 'generate_cloudformation_template':
        suggestions = [
            "Try providing a more specific description of your infrastructure",
            "Include specific AWS service names in your description",
            "Specify the relationships between resources (e.g., 'EC2 instances behind an ALB')"
        ]
        
        if 'invalid group reference' in error_message or 'regex' in error_message:
            suggestions.append("This is a known issue with our template generator that we're working to fix")
        
        return suggestions
    
    # Template validation errors
    if operation == 'validate_template':
        suggestions = [
            "Check the template for syntax errors",
            "Ensure all required properties are specified for each resource",
            "Verify that resource names are unique within the template"
        ]
        
        if 'Requires capabilities' in error_message:
            capabilities = []
            if 'CAPABILITY_IAM' in error_message:
                capabilities.append('CAPABILITY_IAM')
            if 'CAPABILITY_NAMED_IAM' in error_message:
                capabilities.append('CAPABILITY_NAMED_IAM')
            if 'CAPABILITY_AUTO_EXPAND' in error_message:
                capabilities.append('CAPABILITY_AUTO_EXPAND')
            
            capability_str = ', '.join(capabilities)
            suggestions.append(f"Add the following capabilities when deploying: {capability_str}")
        
        return suggestions
    
    # Stack deployment errors
    if operation == 'deploy_simple_stack':
        suggestions = [
            "Validate your template before deployment",
            "Check that you have the necessary permissions to create all resources",
            "Ensure resource names and properties are valid"
        ]
        
        if 'AlreadyExistsException' in error_message:
            suggestions.append("Use a different stack name or update the existing stack")
        
        if 'ValidationError' in error_message and 'No updates are to be performed' in error_message:
            suggestions.append("No changes are needed, the stack is already up to date")
        
        return suggestions
    
    # Generic suggestions
    return [
        "Check your AWS credentials and permissions",
        "Verify that the AWS region is valid and available",
        "Try the operation again with more specific parameters"
    ]