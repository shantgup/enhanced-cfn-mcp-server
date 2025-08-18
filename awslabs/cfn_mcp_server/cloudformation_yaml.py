"""CloudFormation YAML parsing utilities."""

import re
import yaml
import json
from typing import Dict, Any, List, Union, Optional
import tempfile
import os
import subprocess


def parse_cloudformation_template(template_content: str) -> Dict[str, Any]:
    """Parse CloudFormation template content into a dictionary.
    
    Handles both JSON and YAML formats, including CloudFormation intrinsic functions.
    Uses multiple fallback strategies for robust parsing.
    
    Args:
        template_content: Template content as string
        
    Returns:
        Template as dictionary
        
    Raises:
        Exception: If template parsing fails with all strategies
    """
    if not template_content or not template_content.strip():
        raise Exception("Template content is empty")
    
    # Strategy 1: Try parsing as JSON first
    try:
        return json.loads(template_content)
    except json.JSONDecodeError:
        pass
    
    # Strategy 2: Try enhanced YAML parser with CloudFormation intrinsic functions
    try:
        return parse_cloudformation_yaml_with_intrinsics(template_content)
    except (yaml.YAMLError, ValueError, TypeError):
        pass
    
    # Strategy 3: Try fallback YAML parser with preprocessing
    try:
        return parse_cloudformation_yaml_fallback(template_content)
    except (yaml.YAMLError, ValueError, TypeError):
        pass
    
    # Strategy 4: Try basic YAML parsing (ignoring intrinsic functions)
    try:
        result = yaml.safe_load(template_content)
        if isinstance(result, dict):
            return result
    except yaml.YAMLError:
        pass
    
    # Strategy 5: Try to extract basic structure even from malformed templates
    try:
        return extract_basic_template_structure(template_content)
    except (ValueError, TypeError, AttributeError):
        pass
    
    # If all strategies fail, raise an exception
    raise ValueError("Failed to parse CloudFormation template with all available strategies")


def parse_cloudformation_yaml_with_intrinsics(template_content: str) -> Dict[str, Any]:
    """Parse CloudFormation YAML with proper intrinsic function support.
    
    Args:
        template_content: YAML template content
        
    Returns:
        Parsed template dictionary
    """
    # Create a custom YAML loader that handles CloudFormation intrinsic functions
    class CloudFormationLoader(yaml.SafeLoader):
        pass
    
    def ref_constructor(loader, node):
        """Constructor for !Ref tag."""
        return {'Ref': loader.construct_scalar(node)}
    
    def getatt_constructor(loader, node):
        """Constructor for !GetAtt tag."""
        if isinstance(node, yaml.ScalarNode):
            # Handle !GetAtt Resource.Attribute format
            value = loader.construct_scalar(node)
            parts = value.split('.', 1)
            if len(parts) == 2:
                return {'Fn::GetAtt': parts}
            else:
                return {'Fn::GetAtt': [value]}
        elif isinstance(node, yaml.SequenceNode):
            # Handle !GetAtt [Resource, Attribute] format
            return {'Fn::GetAtt': loader.construct_sequence(node)}
        else:
            return {'Fn::GetAtt': loader.construct_object(node)}
    
    def sub_constructor(loader, node):
        """Constructor for !Sub tag."""
        if isinstance(node, yaml.ScalarNode):
            return {'Fn::Sub': loader.construct_scalar(node)}
        elif isinstance(node, yaml.SequenceNode):
            return {'Fn::Sub': loader.construct_sequence(node)}
        else:
            return {'Fn::Sub': loader.construct_object(node)}
    
    def join_constructor(loader, node):
        """Constructor for !Join tag."""
        return {'Fn::Join': loader.construct_sequence(node)}
    
    def select_constructor(loader, node):
        """Constructor for !Select tag."""
        return {'Fn::Select': loader.construct_sequence(node)}
    
    def split_constructor(loader, node):
        """Constructor for !Split tag."""
        return {'Fn::Split': loader.construct_sequence(node)}
    
    def base64_constructor(loader, node):
        """Constructor for !Base64 tag."""
        return {'Fn::Base64': loader.construct_object(node)}
    
    def cidr_constructor(loader, node):
        """Constructor for !Cidr tag."""
        return {'Fn::Cidr': loader.construct_sequence(node)}
    
    def find_in_map_constructor(loader, node):
        """Constructor for !FindInMap tag."""
        return {'Fn::FindInMap': loader.construct_sequence(node)}
    
    def get_azs_constructor(loader, node):
        """Constructor for !GetAZs tag."""
        return {'Fn::GetAZs': loader.construct_object(node)}
    
    def import_value_constructor(loader, node):
        """Constructor for !ImportValue tag."""
        return {'Fn::ImportValue': loader.construct_object(node)}
    
    def condition_constructor(loader, node):
        """Constructor for !Condition tag."""
        return {'Condition': loader.construct_scalar(node)}
    
    def equals_constructor(loader, node):
        """Constructor for !Equals tag."""
        return {'Fn::Equals': loader.construct_sequence(node)}
    
    def if_constructor(loader, node):
        """Constructor for !If tag."""
        return {'Fn::If': loader.construct_sequence(node)}
    
    def not_constructor(loader, node):
        """Constructor for !Not tag."""
        return {'Fn::Not': loader.construct_sequence(node)}
    
    def and_constructor(loader, node):
        """Constructor for !And tag."""
        return {'Fn::And': loader.construct_sequence(node)}
    
    def or_constructor(loader, node):
        """Constructor for !Or tag."""
        return {'Fn::Or': loader.construct_sequence(node)}
    
    # Register constructors for CloudFormation intrinsic functions
    CloudFormationLoader.add_constructor('!Ref', ref_constructor)
    CloudFormationLoader.add_constructor('!GetAtt', getatt_constructor)
    CloudFormationLoader.add_constructor('!Sub', sub_constructor)
    CloudFormationLoader.add_constructor('!Join', join_constructor)
    CloudFormationLoader.add_constructor('!Select', select_constructor)
    CloudFormationLoader.add_constructor('!Split', split_constructor)
    CloudFormationLoader.add_constructor('!Base64', base64_constructor)
    CloudFormationLoader.add_constructor('!Cidr', cidr_constructor)
    CloudFormationLoader.add_constructor('!FindInMap', find_in_map_constructor)
    CloudFormationLoader.add_constructor('!GetAZs', get_azs_constructor)
    CloudFormationLoader.add_constructor('!ImportValue', import_value_constructor)
    CloudFormationLoader.add_constructor('!Condition', condition_constructor)
    CloudFormationLoader.add_constructor('!Equals', equals_constructor)
    CloudFormationLoader.add_constructor('!If', if_constructor)
    CloudFormationLoader.add_constructor('!Not', not_constructor)
    CloudFormationLoader.add_constructor('!And', and_constructor)
    CloudFormationLoader.add_constructor('!Or', or_constructor)
    
    # Parse the YAML with the custom loader
    return yaml.load(template_content, Loader=CloudFormationLoader)


def parse_cloudformation_yaml_fallback(template_content: str) -> Dict[str, Any]:
    """Fallback YAML parser for CloudFormation templates.
    
    This is a more aggressive parser that tries to handle edge cases.
    
    Args:
        template_content: YAML template content
        
    Returns:
        Parsed template dictionary
    """
    try:
        # First, try the intrinsic function parser
        return parse_cloudformation_yaml_with_intrinsics(template_content)
    except (yaml.YAMLError, ValueError, TypeError):
        # If that fails, try the preprocessing approach
        try:
            processed_content = preprocess_cloudformation_yaml(template_content)
            template_dict = yaml.safe_load(processed_content)
            return postprocess_cloudformation_dict(template_dict)
        except (yaml.YAMLError, ValueError, TypeError):
            # Last resort: try to parse as regular YAML and ignore intrinsic functions
            return yaml.safe_load(template_content)


def preprocess_cloudformation_yaml(template_content: str) -> str:
    """Preprocess CloudFormation YAML to handle intrinsic functions.
    
    Args:
        template_content: Template content as string
        
    Returns:
        Preprocessed template content
    """
    # Replace CloudFormation short-form syntax with placeholders that won't break YAML parsing
    # We'll convert these back after parsing
    
    # Create a copy of the content for preprocessing
    processed_content = template_content
    
    # Replace common CloudFormation intrinsic functions with safe placeholders
    # !Ref -> __REF__
    processed_content = re.sub(r'!Ref\s+([\w:.-]+)', r'__REF__: \1', processed_content)
    
    # !GetAtt -> __GETATT__
    processed_content = re.sub(r'!GetAtt\s+([\w:.-]+)\.([\w:.-]+)', r'__GETATT__: [\1, \2]', processed_content)
    
    # !Sub -> __SUB__
    processed_content = re.sub(r'!Sub\s+[\'\"](.*?)[\'"]', r'__SUB__: "\1"', processed_content)
    processed_content = re.sub(r'!Sub\s+([^\s\'""][^\s]*)', r'__SUB__: \1', processed_content)
    
    # !Join -> __JOIN__
    # Fixed regex to avoid backslash escaping issues
    processed_content = re.sub(r'!Join\s+[\'"]([^\'"]*)[\'"],\s*\[(.*?)\]', r'__JOIN__: ["\1", [\2]]', processed_content)
    
    # !ImportValue -> __IMPORTVALUE__
    processed_content = re.sub(r'!ImportValue\s+([\w:.-]+)', r'__IMPORTVALUE__: \1', processed_content)
    
    # !GetAZs -> __GETAZS__
    processed_content = re.sub(r'!GetAZs\s+([\w:.-]+)', r'__GETAZS__: \1', processed_content)
    processed_content = re.sub(r'!GetAZs\s*[\'\"](.*?)[\'"]', r'__GETAZS__: "\1"', processed_content)
    
    # !Select -> __SELECT__
    processed_content = re.sub(r'!Select\s+[\'"](\d+)[\'"],\s*(.*)', r'__SELECT__: ["\1", \2]', processed_content)
    
    return processed_content


def postprocess_cloudformation_dict(template_dict: Dict[str, Any]) -> Dict[str, Any]:
    """Post-process parsed CloudFormation template to restore intrinsic functions.
    
    Args:
        template_dict: Parsed template dictionary
        
    Returns:
        Post-processed template dictionary
    """
    if not isinstance(template_dict, dict):
        return template_dict
    
    result = {}
    for key, value in template_dict.items():
        # Handle special placeholder keys
        if key == '__REF__':
            result = {'Ref': value}
            break
        elif key == '__GETATT__':
            result = {'Fn::GetAtt': value}
            break
        elif key == '__SUB__':
            result = {'Fn::Sub': value}
            break
        elif key == '__JOIN__':
            result = {'Fn::Join': value}
            break
        elif key == '__IMPORTVALUE__':
            result = {'Fn::ImportValue': value}
            break
        elif key == '__GETAZS__':
            result = {'Fn::GetAZs': value}
            break
        elif key == '__SELECT__':
            result = {'Fn::Select': value}
            break
        else:
            # Recursively process nested dictionaries and lists
            if isinstance(value, dict):
                result[key] = postprocess_cloudformation_dict(value)
            elif isinstance(value, list):
                result[key] = [
                    postprocess_cloudformation_dict(item) if isinstance(item, dict) else item
                    for item in value
                ]
            else:
                result[key] = value
    
    return result


def extract_basic_template_structure(template_content: str) -> Dict[str, Any]:
    """Extract basic template structure from malformed templates.
    
    This is a last-resort parser that tries to extract basic CloudFormation
    structure even from templates that can't be parsed normally.
    
    Args:
        template_content: Template content as string
        
    Returns:
        Basic template structure dictionary
    """
    template = {
        "AWSTemplateFormatVersion": "2010-09-09",
        "Resources": {},
        "__parsing_notes": "Template parsed with basic structure extraction"
    }
    
    lines = template_content.split('\n')
    current_section = None
    current_resource = None
    
    for line in lines:
        line = line.strip()
        
        # Skip empty lines and comments
        if not line or line.startswith('#'):
            continue
        
        # Detect main sections
        if line.startswith('AWSTemplateFormatVersion:'):
            template["AWSTemplateFormatVersion"] = line.split(':', 1)[1].strip().strip('"\'')
        elif line.startswith('Description:'):
            template["Description"] = line.split(':', 1)[1].strip().strip('"\'')
        elif line == 'Parameters:':
            current_section = 'Parameters'
            template["Parameters"] = {}
        elif line == 'Resources:':
            current_section = 'Resources'
            template["Resources"] = {}
        elif line == 'Outputs:':
            current_section = 'Outputs'
            template["Outputs"] = {}
        elif current_section == 'Resources' and ':' in line and not line.startswith(' '):
            # New resource
            resource_name = line.split(':')[0].strip()
            template["Resources"][resource_name] = {
                "Type": "AWS::Unknown::Resource",
                "Properties": {}
            }
            current_resource = resource_name
        elif current_section == 'Resources' and current_resource and line.startswith('Type:'):
            resource_type = line.split(':', 1)[1].strip().strip('"\'')
            template["Resources"][current_resource]["Type"] = resource_type
    
    return template


def coerce_template_content(content: Any) -> str:
    """Coerce template content to string format.
    
    Args:
        content: Template content (string or dict)
        
    Returns:
        Template content as string
    """
    if isinstance(content, dict):
        return json.dumps(content)
    elif content is None:
        raise ValueError("Template content cannot be None")
    return str(content)