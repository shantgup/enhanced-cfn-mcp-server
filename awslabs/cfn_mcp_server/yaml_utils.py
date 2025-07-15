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

"""YAML utilities for CloudFormation templates."""

import yaml
import re
from typing import Dict, Any, List, Union


class CloudFormationYamlDumper(yaml.SafeDumper):
    """Custom YAML dumper for CloudFormation templates with consistent syntax."""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.use_short_form = True  # Set to False to use long-form syntax
    
    def represent_mapping(self, tag, mapping, flow_style=None):
        """Override to handle CloudFormation intrinsic functions consistently."""
        # Check if this is a CloudFormation intrinsic function
        if len(mapping) == 1:
            key = list(mapping.keys())[0]
            if key in ['Ref', 'Fn::GetAtt', 'Fn::Sub', 'Fn::Join', 'Fn::Select', 'Fn::ImportValue',
                      'Fn::GetAZs', 'Fn::Split', 'Fn::FindInMap', 'Fn::Base64', 'Fn::Cidr',
                      'Fn::Transform', 'Fn::If', 'Fn::Equals', 'Fn::Not', 'Fn::And', 'Fn::Or']:
                if self.use_short_form:
                    # Convert to short form
                    if key == 'Ref':
                        return self.represent_scalar('!Ref', mapping[key])
                    elif key == 'Fn::GetAtt':
                        if isinstance(mapping[key], list):
                            return self.represent_scalar('!GetAtt', '.'.join(mapping[key]))
                        else:
                            return self.represent_scalar('!GetAtt', mapping[key])
                    elif key == 'Fn::Sub':
                        return self.represent_scalar('!Sub', mapping[key])
                    elif key == 'Fn::Join':
                        if isinstance(mapping[key], list) and len(mapping[key]) == 2:
                            delimiter, values = mapping[key]
                            if isinstance(values, list):
                                return self.represent_scalar('!Join', f"{delimiter}, {values}")
                    elif key == 'Fn::ImportValue':
                        return self.represent_scalar('!ImportValue', mapping[key])
                    elif key == 'Fn::GetAZs':
                        return self.represent_scalar('!GetAZs', mapping[key])
                    # Add more intrinsic functions as needed
        
        # Default behavior for other mappings
        return super().represent_mapping(tag, mapping, flow_style)


def dump_cloudformation_yaml(template: Dict[str, Any], use_short_form: bool = True) -> str:
    """Dump CloudFormation template to YAML with consistent syntax.
    
    Args:
        template: CloudFormation template as dictionary
        use_short_form: Whether to use short-form (!Ref) or long-form (Ref:) syntax
        
    Returns:
        YAML string with consistent syntax
    """
    dumper = CloudFormationYamlDumper
    dumper.use_short_form = use_short_form
    
    # Register representers for CloudFormation intrinsic functions
    yaml.add_representer(dict, dumper.represent_dict, Dumper=dumper)
    
    # Dump template to YAML
    yaml_str = yaml.dump(template, Dumper=dumper, default_flow_style=False, sort_keys=False)
    
    # Post-process to fix any remaining inconsistencies
    if use_short_form:
        # Convert any remaining long-form syntax to short-form
        yaml_str = re.sub(r'Ref:\s+(\w+)', r'!Ref \1', yaml_str)
        yaml_str = re.sub(r'Fn::GetAtt:\s+\[\s*\'?(\w+)\'?,\s*\'?(\w+)\'?\s*\]', r'!GetAtt \1.\2', yaml_str)
        yaml_str = re.sub(r'Fn::Sub:\s+\'(.+?)\'', r'!Sub \'\1\'', yaml_str)
    else:
        # Convert any short-form syntax to long-form
        yaml_str = re.sub(r'!Ref\s+(\w+)', r'Ref: \1', yaml_str)
        yaml_str = re.sub(r'!GetAtt\s+(\w+)\.(\w+)', r'Fn::GetAtt: [\1, \2]', yaml_str)
        yaml_str = re.sub(r'!Sub\s+\'(.+?)\'', r'Fn::Sub: \'\1\'', yaml_str)
    
    return yaml_str


def convert_to_consistent_syntax(template_content: str, use_short_form: bool = True) -> str:
    """Convert an existing template to use consistent syntax.
    
    Args:
        template_content: Template content as string
        use_short_form: Whether to use short-form (!Ref) or long-form (Ref:) syntax
        
    Returns:
        Template content with consistent syntax
    """
    # Parse template
    template = yaml.safe_load(template_content)
    
    # Dump with consistent syntax
    return dump_cloudformation_yaml(template, use_short_form)