"""Input validation framework for CloudFormation MCP server."""

import re
import json
import yaml
from typing import Any, Dict, List, Optional, Union
from functools import wraps


class ValidationError(Exception):
    """Raised when input validation fails."""
    pass


class InputValidator:
    """Validates user inputs for security and correctness."""
    
    # AWS resource type pattern: AWS::Service::Resource
    AWS_RESOURCE_TYPE_PATTERN = re.compile(r'^AWS::[A-Za-z0-9]+::[A-Za-z0-9]+$')
    
    # AWS region pattern: us-east-1, eu-west-1, etc.
    AWS_REGION_PATTERN = re.compile(r'^[a-z]{2}-[a-z]+-\d+$')
    
    # CloudFormation stack name pattern
    STACK_NAME_PATTERN = re.compile(r'^[a-zA-Z][-a-zA-Z0-9]*$')
    
    # Maximum sizes
    MAX_TEMPLATE_SIZE = 1024 * 1024  # 1MB
    MAX_DESCRIPTION_LENGTH = 10000
    MAX_STACK_NAME_LENGTH = 128
    MAX_IDENTIFIER_LENGTH = 256
    
    @staticmethod
    def validate_aws_resource_type(resource_type: str) -> str:
        """Validate AWS resource type format."""
        if not resource_type:
            raise ValidationError("Resource type cannot be empty")
        
        if not isinstance(resource_type, str):
            raise ValidationError("Resource type must be a string")
        
        if len(resource_type) > 100:
            raise ValidationError("Resource type too long")
        
        if not InputValidator.AWS_RESOURCE_TYPE_PATTERN.match(resource_type):
            raise ValidationError(f"Invalid AWS resource type format: {resource_type}")
        
        return resource_type
    
    @staticmethod
    def validate_aws_region(region: Optional[str]) -> Optional[str]:
        """Validate AWS region format."""
        if region is None:
            return None
        
        if not isinstance(region, str):
            raise ValidationError("Region must be a string")
        
        if not InputValidator.AWS_REGION_PATTERN.match(region):
            raise ValidationError(f"Invalid AWS region format: {region}")
        
        return region
    
    @staticmethod
    def validate_stack_name(stack_name: str) -> str:
        """Validate CloudFormation stack name."""
        if not stack_name:
            raise ValidationError("Stack name cannot be empty")
        
        if not isinstance(stack_name, str):
            raise ValidationError("Stack name must be a string")
        
        if len(stack_name) > InputValidator.MAX_STACK_NAME_LENGTH:
            raise ValidationError(f"Stack name too long (max {InputValidator.MAX_STACK_NAME_LENGTH} chars)")
        
        if not InputValidator.STACK_NAME_PATTERN.match(stack_name):
            raise ValidationError(f"Invalid stack name format: {stack_name}")
        
        return stack_name
    
    @staticmethod
    def validate_identifier(identifier: str) -> str:
        """Validate resource identifier."""
        if not identifier:
            raise ValidationError("Identifier cannot be empty")
        
        if not isinstance(identifier, str):
            raise ValidationError("Identifier must be a string")
        
        if len(identifier) > InputValidator.MAX_IDENTIFIER_LENGTH:
            raise ValidationError(f"Identifier too long (max {InputValidator.MAX_IDENTIFIER_LENGTH} chars)")
        
        # Basic sanitization - remove control characters
        if any(ord(c) < 32 for c in identifier if c not in '\t\n\r'):
            raise ValidationError("Identifier contains invalid control characters")
        
        return identifier
    
    @staticmethod
    def validate_template_content(template_content: str) -> str:
        """Validate CloudFormation template content."""
        if not template_content:
            raise ValidationError("Template content cannot be empty")
        
        if not isinstance(template_content, str):
            raise ValidationError("Template content must be a string")
        
        if len(template_content) > InputValidator.MAX_TEMPLATE_SIZE:
            raise ValidationError(f"Template too large (max {InputValidator.MAX_TEMPLATE_SIZE} bytes)")
        
        # Try to parse as YAML or JSON
        try:
            # Try YAML first
            yaml.safe_load(template_content)
        except yaml.YAMLError:
            try:
                # Try JSON
                json.loads(template_content)
            except json.JSONDecodeError:
                raise ValidationError("Template content is not valid YAML or JSON")
        
        return template_content
    
    @staticmethod
    def validate_description(description: str) -> str:
        """Validate description text."""
        if not description:
            raise ValidationError("Description cannot be empty")
        
        if not isinstance(description, str):
            raise ValidationError("Description must be a string")
        
        if len(description) > InputValidator.MAX_DESCRIPTION_LENGTH:
            raise ValidationError(f"Description too long (max {InputValidator.MAX_DESCRIPTION_LENGTH} chars)")
        
        # Basic sanitization - remove control characters except common ones
        if any(ord(c) < 32 for c in description if c not in '\t\n\r'):
            raise ValidationError("Description contains invalid control characters")
        
        return description
    
    @staticmethod
    def validate_properties(properties: Dict[str, Any]) -> Dict[str, Any]:
        """Validate resource properties dictionary."""
        if not isinstance(properties, dict):
            raise ValidationError("Properties must be a dictionary")
        
        # Convert to JSON and back to ensure it's serializable
        try:
            json_str = json.dumps(properties)
            if len(json_str) > InputValidator.MAX_TEMPLATE_SIZE:
                raise ValidationError("Properties too large")
            return json.loads(json_str)
        except (TypeError, ValueError) as e:
            raise ValidationError(f"Properties not serializable: {e}")
    
    @staticmethod
    def validate_patch_document(patch_document: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Validate JSON patch document."""
        if not isinstance(patch_document, list):
            raise ValidationError("Patch document must be a list")
        
        for i, patch in enumerate(patch_document):
            if not isinstance(patch, dict):
                raise ValidationError(f"Patch {i} must be a dictionary")
            
            if 'op' not in patch:
                raise ValidationError(f"Patch {i} missing 'op' field")
            
            if patch['op'] not in ['add', 'remove', 'replace', 'move', 'copy', 'test']:
                raise ValidationError(f"Patch {i} has invalid operation: {patch['op']}")
        
        return patch_document


def validate_input(**validators):
    """Decorator to validate function inputs."""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Validate each specified parameter
            for param_name, validator_func in validators.items():
                if param_name in kwargs:
                    try:
                        kwargs[param_name] = validator_func(kwargs[param_name])
                    except ValidationError as e:
                        raise ValidationError(f"Invalid {param_name}: {e}")
            
            return func(*args, **kwargs)
        return wrapper
    return decorator


# Singleton instance
_input_validator = InputValidator()

def get_input_validator() -> InputValidator:
    """Get the singleton input validator instance."""
    return _input_validator
