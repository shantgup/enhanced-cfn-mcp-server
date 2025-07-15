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

"""CloudFormation template validation utilities."""

import json
import yaml
from typing import Dict, List, Any, Optional, Tuple
from awslabs.cfn_mcp_server.aws_client import get_aws_client
from awslabs.cfn_mcp_server.errors import ClientError


async def validate_template(template_content: str, region: Optional[str] = None) -> Dict[str, Any]:
    """Validate a CloudFormation template.
    
    Args:
        template_content: The template content as a string (JSON or YAML)
        region: Optional AWS region
        
    Returns:
        Dictionary with validation results
    """
    try:
        # Parse the template to check for syntax errors
        template_dict = _parse_template(template_content)
        
        # Perform local validation checks
        local_validation = _validate_template_locally(template_dict)
        
        # Validate with CloudFormation API
        api_validation = await _validate_template_with_api(template_content, region)
        
        # Combine results
        return {
            'valid': local_validation['valid'] and api_validation['valid'],
            'local_validation': local_validation,
            'api_validation': api_validation,
            'capabilities_required': api_validation.get('capabilities_required', []),
            'parameters': api_validation.get('parameters', [])
        }
    except Exception as e:
        return {
            'valid': False,
            'error': str(e),
            'message': 'Template validation failed'
        }


def _parse_template(template_content: str) -> Dict[str, Any]:
    """Parse template content into a dictionary.
    
    Args:
        template_content: Template content as string
        
    Returns:
        Template as dictionary
        
    Raises:
        ClientError: If template parsing fails
    """
    try:
        # Use the enhanced CloudFormation YAML parser
        from awslabs.cfn_mcp_server.cloudformation_yaml import parse_cloudformation_template
        return parse_cloudformation_template(template_content)
    except Exception as e:
        raise ClientError(f"Template parsing failed: {str(e)}")


def _validate_template_locally(template: Dict[str, Any]) -> Dict[str, Any]:
    """Perform local validation checks on the template.
    
    Args:
        template: Template as dictionary
        
    Returns:
        Dictionary with validation results
    """
    issues = []
    warnings = []
    
    # Check template size (CloudFormation limit is 51,200 bytes)
    template_size = len(json.dumps(template))
    if template_size > 51200:
        issues.append(f"Template size ({template_size} bytes) exceeds CloudFormation limit of 51,200 bytes")
    elif template_size > 40000:
        warnings.append(f"Template size ({template_size} bytes) is approaching CloudFormation limit of 51,200 bytes")
    
    # Check for required sections
    if 'Resources' not in template:
        issues.append("Template is missing required 'Resources' section")
    elif not template['Resources']:
        issues.append("'Resources' section is empty")
    
    # Check resource count (CloudFormation limit is 500 resources)
    resource_count = len(template.get('Resources', {}))
    if resource_count > 500:
        issues.append(f"Template contains {resource_count} resources, exceeding CloudFormation limit of 500")
    elif resource_count > 400:
        warnings.append(f"Template contains {resource_count} resources, approaching CloudFormation limit of 500")
    elif resource_count == 0:
        issues.append("Template contains no resources")
    
    # Check for circular dependencies
    dependency_issues = _check_circular_dependencies(template)
    issues.extend(dependency_issues)
    
    # Check for security best practices
    security_issues, security_warnings = _check_security_best_practices(template)
    issues.extend(security_issues)
    warnings.extend(security_warnings)
    
    return {
        'valid': len(issues) == 0,
        'issues': issues,
        'warnings': warnings,
        'resource_count': resource_count,
        'template_size_bytes': template_size
    }


def _check_circular_dependencies(template: Dict[str, Any]) -> List[str]:
    """Check for circular dependencies in the template.
    
    Args:
        template: Template as dictionary
        
    Returns:
        List of issues found
    """
    issues = []
    resources = template.get('Resources', {})
    
    # Build dependency graph
    dependency_graph = {}
    for resource_id, resource in resources.items():
        dependencies = []
        
        # Check DependsOn
        depends_on = resource.get('DependsOn', [])
        if isinstance(depends_on, str):
            dependencies.append(depends_on)
        elif isinstance(depends_on, list):
            dependencies.extend(depends_on)
        
        # Check Ref and Fn::GetAtt in Properties
        properties = resource.get('Properties', {})
        refs = _find_refs_in_properties(properties)
        dependencies.extend(refs)
        
        dependency_graph[resource_id] = dependencies
    
    # Check for circular dependencies
    visited = set()
    temp_visited = set()
    
    def has_cycle(node, path=None):
        if path is None:
            path = []
        
        if node in temp_visited:
            cycle_path = path + [node]
            issues.append(f"Circular dependency detected: {' -> '.join(cycle_path)}")
            return True
        
        if node in visited:
            return False
        
        temp_visited.add(node)
        path.append(node)
        
        for dependency in dependency_graph.get(node, []):
            if dependency in resources and has_cycle(dependency, path):
                return True
        
        temp_visited.remove(node)
        path.pop()
        visited.add(node)
        return False
    
    for resource_id in resources:
        has_cycle(resource_id)
    
    return issues


def _find_refs_in_properties(properties: Dict[str, Any]) -> List[str]:
    """Find Ref and GetAtt references in properties.
    
    Args:
        properties: Resource properties
        
    Returns:
        List of referenced resource IDs
    """
    refs = []
    
    if isinstance(properties, dict):
        for key, value in properties.items():
            if key == 'Ref' and isinstance(value, str) and not value.startswith('AWS::'):
                refs.append(value)
            elif key == 'Fn::GetAtt' and isinstance(value, list) and len(value) >= 1:
                refs.append(value[0])
            elif isinstance(value, dict):
                refs.extend(_find_refs_in_properties(value))
            elif isinstance(value, list):
                for item in value:
                    if isinstance(item, dict):
                        refs.extend(_find_refs_in_properties(item))
    
    return refs


def _check_security_best_practices(template: Dict[str, Any]) -> Tuple[List[str], List[str]]:
    """Check for security best practices in the template.
    
    Args:
        template: Template as dictionary
        
    Returns:
        Tuple of (issues, warnings)
    """
    issues = []
    warnings = []
    resources = template.get('Resources', {})
    
    # Check for overly permissive security groups
    for resource_id, resource in resources.items():
        if resource.get('Type') == 'AWS::EC2::SecurityGroup':
            properties = resource.get('Properties', {})
            ingress_rules = properties.get('SecurityGroupIngress', [])
            
            for rule in ingress_rules:
                if rule.get('CidrIp') == '0.0.0.0/0' and rule.get('IpProtocol') != 'icmp':
                    port_range = f"{rule.get('FromPort', 'all')}-{rule.get('ToPort', 'all')}"
                    if port_range in ['22-22', '3389-3389']:
                        issues.append(f"Security group {resource_id} allows unrestricted SSH/RDP access from the internet")
                    else:
                        warnings.append(f"Security group {resource_id} allows unrestricted access on ports {port_range}")
    
    # Check for unencrypted storage
    for resource_id, resource in resources.items():
        if resource.get('Type') == 'AWS::RDS::DBInstance':
            properties = resource.get('Properties', {})
            if not properties.get('StorageEncrypted', False):
                issues.append(f"RDS instance {resource_id} does not have storage encryption enabled")
        
        elif resource.get('Type') == 'AWS::S3::Bucket':
            properties = resource.get('Properties', {})
            if 'BucketEncryption' not in properties:
                warnings.append(f"S3 bucket {resource_id} does not have default encryption configured")
    
    # Check for IAM roles with overly permissive policies
    for resource_id, resource in resources.items():
        if resource.get('Type') == 'AWS::IAM::Policy' or resource.get('Type') == 'AWS::IAM::ManagedPolicy':
            properties = resource.get('Properties', {})
            policy_document = properties.get('PolicyDocument', {})
            
            for statement in policy_document.get('Statement', []):
                if statement.get('Effect') == 'Allow' and statement.get('Action') == '*' and statement.get('Resource') == '*':
                    issues.append(f"IAM policy {resource_id} has overly permissive '*:*' permissions")
    
    return issues, warnings


async def _validate_template_with_api(template_content: str, region: Optional[str] = None) -> Dict[str, Any]:
    """Validate template using CloudFormation API.
    
    Args:
        template_content: Template content as string
        region: Optional AWS region
        
    Returns:
        Dictionary with validation results
    """
    try:
        client = get_aws_client('cloudformation', region)
        response = client.validate_template(TemplateBody=template_content)
        
        # Extract capabilities and parameters
        capabilities = response.get('Capabilities', [])
        parameters = response.get('Parameters', [])
        
        return {
            'valid': True,
            'capabilities_required': capabilities,
            'parameters': parameters
        }
    except Exception as e:
        return {
            'valid': False,
            'error': str(e),
            'message': 'CloudFormation API validation failed'
        }