"""CloudFormation template capabilities detection."""

import re
import json
from typing import Dict, Any, List, Set, Optional


def detect_required_capabilities(template: Dict[str, Any]) -> List[str]:
    """Detect required capabilities for a CloudFormation template.
    
    Args:
        template: CloudFormation template as dictionary
        
    Returns:
        List of required capabilities
    """
    capabilities = set()
    
    # Check for IAM resources
    if _contains_iam_resources(template):
        capabilities.add('CAPABILITY_IAM')
    
    # Check for named IAM resources
    if _contains_named_iam_resources(template):
        capabilities.add('CAPABILITY_NAMED_IAM')
    
    # Check for macros and transforms
    if _contains_transforms(template):
        capabilities.add('CAPABILITY_AUTO_EXPAND')
    
    return list(capabilities)


def _contains_iam_resources(template: Dict[str, Any]) -> bool:
    """Check if template contains IAM resources.
    
    Args:
        template: CloudFormation template as dictionary
        
    Returns:
        True if template contains IAM resources
    """
    resources = template.get('Resources', {})
    
    # Check for IAM resource types
    for resource in resources.values():
        resource_type = resource.get('Type', '')
        if resource_type.startswith('AWS::IAM::'):
            return True
    
    # Check for IAM policy documents in other resources
    template_str = json.dumps(template)
    if '"PolicyDocument"' in template_str or '"AssumeRolePolicyDocument"' in template_str:
        return True
    
    return False


def _contains_named_iam_resources(template: Dict[str, Any]) -> bool:
    """Check if template contains named IAM resources.
    
    Args:
        template: CloudFormation template as dictionary
        
    Returns:
        True if template contains named IAM resources
    """
    resources = template.get('Resources', {})
    
    # Check for named IAM resources
    for resource in resources.values():
        resource_type = resource.get('Type', '')
        if resource_type in ['AWS::IAM::Role', 'AWS::IAM::User', 'AWS::IAM::Group']:
            properties = resource.get('Properties', {})
            if 'RoleName' in properties or 'UserName' in properties or 'GroupName' in properties:
                return True
    
    return False


def _contains_transforms(template: Dict[str, Any]) -> bool:
    """Check if template contains transforms or macros.
    
    Args:
        template: CloudFormation template as dictionary
        
    Returns:
        True if template contains transforms or macros
    """
    # Check for Transform section
    if 'Transform' in template:
        return True
    
    # Check for Fn::Transform function
    template_str = json.dumps(template)
    if '"Fn::Transform"' in template_str:
        return True
    
    return False


def detect_template_parameters(template: Dict[str, Any]) -> Dict[str, Dict[str, Any]]:
    """Detect parameters in a CloudFormation template.
    
    Args:
        template: CloudFormation template as dictionary
        
    Returns:
        Dictionary of parameter names to parameter definitions
    """
    parameters = template.get('Parameters', {})
    return parameters


def detect_template_outputs(template: Dict[str, Any]) -> Dict[str, Dict[str, Any]]:
    """Detect outputs in a CloudFormation template.
    
    Args:
        template: CloudFormation template as dictionary
        
    Returns:
        Dictionary of output names to output definitions
    """
    outputs = template.get('Outputs', {})
    return outputs