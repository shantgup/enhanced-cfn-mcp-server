"""
Enhanced CloudFormation Template Fixer Module

This module automatically fixes issues identified in CloudFormation templates
by the TemplateAnalyzer, applying best practices and resolving common problems.
"""

import json
import copy
from typing import Dict, List, Any, Optional, Tuple
try:
    import yaml
except ImportError:
    yaml = None
import uuid
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
import logging

from .template_analyzer import TemplateIssue, TemplateAnalyzer

logger = logging.getLogger(__name__)

@dataclass
class TemplateFix:
    """Represents a fix applied to a template"""
    fix_id: str
    resource_id: str
    fix_type: str
    description: str
    original_value: Any
    new_value: Any
    confidence: str  # HIGH, MEDIUM, LOW
    reversible: bool = True

class TemplateFixer:
    """Automatically fixes CloudFormation template issues"""
    
    def __init__(self):
        self.applied_fixes = []
        self.fix_strategies = self._load_fix_strategies()
        self.best_practices = self._load_best_practices()
    
    def fix_template(self, template: Dict[str, Any], analysis: Dict[str, Any], 
                    auto_apply: bool = True, max_fixes: int = 50) -> Dict[str, Any]:
        """
        Fix template issues based on analysis results
        
        Args:
            template: Original CloudFormation template
            analysis: Analysis results from TemplateAnalyzer
            auto_apply: Whether to automatically apply high-confidence fixes
            max_fixes: Maximum number of fixes to apply
            
        Returns:
            Dictionary with fixed template and fix details
        """
        try:
            result = {
                'fixed_template': copy.deepcopy(template),
                'fixes_applied': [],
                'fixes_skipped': [],
                'success': True,
                'backup_template': copy.deepcopy(template)
            }
            
            fixes_applied = 0
            
            # Fix high-priority issues first
            issues = analysis.get('issues', [])
            prioritized_issues = self._prioritize_issues(issues)
            
            for issue in prioritized_issues:
                if fixes_applied >= max_fixes:
                    break
                    
                fix_result = self._apply_fix_for_issue(
                    result['fixed_template'], 
                    issue, 
                    auto_apply
                )
                
                if fix_result['applied']:
                    result['fixes_applied'].append(fix_result['fix'])
                    fixes_applied += 1
                else:
                    result['fixes_skipped'].append({
                        'issue': issue,
                        'reason': fix_result.get('reason', 'Unknown')
                    })
            
            # Apply missing components
            missing_components = analysis.get('missing_components', [])
            for component in missing_components:
                if fixes_applied >= max_fixes:
                    break
                    
                fix_result = self._add_missing_component(
                    result['fixed_template'], 
                    component, 
                    auto_apply
                )
                
                if fix_result['applied']:
                    result['fixes_applied'].append(fix_result['fix'])
                    fixes_applied += 1
            
            # Apply security fixes
            security_issues = analysis.get('security_issues', [])
            for security_issue in security_issues:
                if fixes_applied >= max_fixes:
                    break
                    
                fix_result = self._fix_security_issue(
                    result['fixed_template'], 
                    security_issue, 
                    auto_apply
                )
                
                if fix_result['applied']:
                    result['fixes_applied'].append(fix_result['fix'])
                    fixes_applied += 1
            
            # Apply best practices
            if auto_apply:
                best_practice_fixes = self._apply_best_practices(
                    result['fixed_template'], 
                    analysis
                )
                result['fixes_applied'].extend(best_practice_fixes)
            
            # Validate fixed template
            analyzer = TemplateAnalyzer()
            validation_result = analyzer.analyze_template(result['fixed_template'])
            result['validation'] = validation_result
            
            logger.info(f"Applied {len(result['fixes_applied'])} fixes to template")
            return result
            
        except Exception as e:
            logger.exception(f"Error fixing template: {e}")
            return {
                'fixed_template': template,
                'fixes_applied': [],
                'fixes_skipped': [],
                'success': False,
                'error': str(e)
            }
    
    def fix_specific_failure(self, template: Dict[str, Any], failure_reason: str, 
                           resource_id: str) -> Dict[str, Any]:
        """
        Fix template based on specific CloudFormation failure
        
        Args:
            template: CloudFormation template
            failure_reason: CloudFormation failure reason
            resource_id: Failed resource ID
            
        Returns:
            Fixed template and applied fixes
        """
        try:
            result = {
                'fixed_template': copy.deepcopy(template),
                'fixes_applied': [],
                'success': True
            }
            
            # Analyze failure reason and apply targeted fix
            fix_strategy = self._get_failure_fix_strategy(failure_reason, resource_id)
            
            if fix_strategy:
                fix_result = self._apply_failure_fix(
                    result['fixed_template'], 
                    fix_strategy, 
                    resource_id
                )
                
                if fix_result['applied']:
                    result['fixes_applied'].append(fix_result['fix'])
                else:
                    result['success'] = False
                    result['error'] = fix_result.get('reason', 'Failed to apply fix')
            
            return result
            
        except Exception as e:
            logger.exception(f"Error fixing specific failure: {e}")
            return {
                'fixed_template': template,
                'fixes_applied': [],
                'success': False,
                'error': str(e)
            }
    
    def _prioritize_issues(self, issues: List[TemplateIssue]) -> List[TemplateIssue]:
        """Prioritize issues for fixing"""
        priority_order = {
            'HIGH': 3,
            'MEDIUM': 2,
            'LOW': 1
        }
        
        return sorted(issues, key=lambda x: priority_order.get(x.severity, 0), reverse=True)
    
    def _apply_fix_for_issue(self, template: Dict[str, Any], issue: TemplateIssue, 
                           auto_apply: bool) -> Dict[str, Any]:
        """Apply fix for a specific template issue"""
        try:
            fix_strategy = self.fix_strategies.get(issue.issue_type)
            
            if not fix_strategy:
                return {
                    'applied': False,
                    'reason': f'No fix strategy for issue type: {issue.issue_type}'
                }
            
            # Check if we should auto-apply this fix
            if not auto_apply and fix_strategy.get('confidence', 'LOW') != 'HIGH':
                return {
                    'applied': False,
                    'reason': 'Auto-apply disabled for medium/low confidence fixes'
                }
            
            # Apply the fix
            fix_result = self._execute_fix_strategy(template, issue, fix_strategy)
            
            if fix_result['success']:
                fix = TemplateFix(
                    fix_id=str(uuid.uuid4()),
                    resource_id=issue.resource_id,
                    fix_type=issue.issue_type,
                    description=fix_result['description'],
                    original_value=fix_result.get('original_value'),
                    new_value=fix_result.get('new_value'),
                    confidence=fix_strategy.get('confidence', 'MEDIUM')
                )
                
                return {
                    'applied': True,
                    'fix': fix
                }
            else:
                return {
                    'applied': False,
                    'reason': fix_result.get('error', 'Fix execution failed')
                }
                
        except Exception as e:
            logger.exception(f"Error applying fix for issue: {e}")
            return {
                'applied': False,
                'reason': str(e)
            }
    
    def _execute_fix_strategy(self, template: Dict[str, Any], issue: TemplateIssue, 
                            strategy: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a specific fix strategy"""
        try:
            strategy_type = strategy.get('type')
            
            if strategy_type == 'ADD_PROPERTY':
                return self._add_property_fix(template, issue, strategy)
            elif strategy_type == 'MODIFY_PROPERTY':
                return self._modify_property_fix(template, issue, strategy)
            elif strategy_type == 'ADD_RESOURCE':
                return self._add_resource_fix(template, issue, strategy)
            elif strategy_type == 'REMOVE_PROPERTY':
                return self._remove_property_fix(template, issue, strategy)
            elif strategy_type == 'ADD_TEMPLATE_SECTION':
                return self._add_template_section_fix(template, issue, strategy)
            else:
                return {
                    'success': False,
                    'error': f'Unknown fix strategy type: {strategy_type}'
                }
                
        except Exception as e:
            logger.exception(f"Error executing fix strategy: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def _add_property_fix(self, template: Dict[str, Any], issue: TemplateIssue, 
                         strategy: Dict[str, Any]) -> Dict[str, Any]:
        """Add missing property to resource"""
        try:
            resource_id = issue.resource_id
            property_path = strategy.get('property_path')
            property_value = strategy.get('property_value')
            
            if resource_id == 'TEMPLATE':
                # Template-level property
                if property_path == 'AWSTemplateFormatVersion':
                    template['AWSTemplateFormatVersion'] = property_value
                    return {
                        'success': True,
                        'description': f'Added {property_path} to template',
                        'original_value': None,
                        'new_value': property_value
                    }
            else:
                # Resource property
                if resource_id not in template.get('Resources', {}):
                    return {
                        'success': False,
                        'error': f'Resource {resource_id} not found'
                    }
                
                resource = template['Resources'][resource_id]
                if 'Properties' not in resource:
                    resource['Properties'] = {}
                
                # Handle nested property paths
                path_parts = property_path.split('.')
                current = resource['Properties']
                
                for part in path_parts[:-1]:
                    if part not in current:
                        current[part] = {}
                    current = current[part]
                
                original_value = current.get(path_parts[-1])
                current[path_parts[-1]] = property_value
                
                return {
                    'success': True,
                    'description': f'Added {property_path} to {resource_id}',
                    'original_value': original_value,
                    'new_value': property_value
                }
                
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def _modify_property_fix(self, template: Dict[str, Any], issue: TemplateIssue, 
                           strategy: Dict[str, Any]) -> Dict[str, Any]:
        """Modify existing property value"""
        try:
            resource_id = issue.resource_id
            property_path = strategy.get('property_path')
            property_value = strategy.get('property_value')
            
            if resource_id not in template.get('Resources', {}):
                return {
                    'success': False,
                    'error': f'Resource {resource_id} not found'
                }
            
            resource = template['Resources'][resource_id]
            properties = resource.get('Properties', {})
            
            # Handle nested property paths
            path_parts = property_path.split('.')
            current = properties
            
            for part in path_parts[:-1]:
                if part not in current:
                    return {
                        'success': False,
                        'error': f'Property path {property_path} not found'
                    }
                current = current[part]
            
            original_value = current.get(path_parts[-1])
            current[path_parts[-1]] = property_value
            
            return {
                'success': True,
                'description': f'Modified {property_path} in {resource_id}',
                'original_value': original_value,
                'new_value': property_value
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def _add_resource_fix(self, template: Dict[str, Any], issue: TemplateIssue, 
                         strategy: Dict[str, Any]) -> Dict[str, Any]:
        """Add missing resource to template"""
        try:
            resource_template = strategy.get('resource_template')
            resource_name = strategy.get('resource_name')
            
            if not resource_template or not resource_name:
                return {
                    'success': False,
                    'error': 'Missing resource template or name'
                }
            
            if 'Resources' not in template:
                template['Resources'] = {}
            
            # Generate unique resource name if needed
            if resource_name in template['Resources']:
                resource_name = f"{resource_name}{uuid.uuid4().hex[:8]}"
            
            template['Resources'][resource_name] = resource_template
            
            return {
                'success': True,
                'description': f'Added resource {resource_name}',
                'original_value': None,
                'new_value': resource_template
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def _add_missing_component(self, template: Dict[str, Any], component: Dict[str, Any], 
                             auto_apply: bool) -> Dict[str, Any]:
        """Add missing component to template"""
        try:
            component_type = component.get('component')
            
            if component_type == 'Lambda Execution Role':
                return self._add_lambda_execution_role(template)
            elif component_type == 'API Gateway Methods':
                return self._add_api_gateway_methods(template)
            else:
                return {
                    'applied': False,
                    'reason': f'No handler for component type: {component_type}'
                }
                
        except Exception as e:
            logger.exception(f"Error adding missing component: {e}")
            return {
                'applied': False,
                'reason': str(e)
            }
    
    def _add_lambda_execution_role(self, template: Dict[str, Any]) -> Dict[str, Any]:
        """Add Lambda execution role to template"""
        try:
            role_name = f"LambdaExecutionRole{uuid.uuid4().hex[:8]}"
            
            execution_role = {
                'Type': 'AWS::IAM::Role',
                'Properties': {
                    'AssumeRolePolicyDocument': {
                        'Version': '2012-10-17',
                        'Statement': [{
                            'Effect': 'Allow',
                            'Principal': {'Service': 'lambda.amazonaws.com'},
                            'Action': 'sts:AssumeRole'
                        }]
                    },
                    'ManagedPolicyArns': [
                        'arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole'
                    ]
                }
            }
            
            if 'Resources' not in template:
                template['Resources'] = {}
            
            template['Resources'][role_name] = execution_role
            
            # Update Lambda functions to use this role
            for resource_id, resource in template['Resources'].items():
                if resource.get('Type') == 'AWS::Lambda::Function':
                    properties = resource.get('Properties', {})
                    if 'Role' not in properties:
                        properties['Role'] = {'Fn::GetAtt': [role_name, 'Arn']}
            
            fix = TemplateFix(
                fix_id=str(uuid.uuid4()),
                resource_id=role_name,
                fix_type='ADD_MISSING_COMPONENT',
                description=f'Added Lambda execution role {role_name}',
                original_value=None,
                new_value=execution_role,
                confidence='HIGH'
            )
            
            return {
                'applied': True,
                'fix': fix
            }
            
        except Exception as e:
            return {
                'applied': False,
                'reason': str(e)
            }
    
    def _fix_security_issue(self, template: Dict[str, Any], security_issue: Dict[str, Any], 
                          auto_apply: bool) -> Dict[str, Any]:
        """Fix security issue in template"""
        try:
            issue_type = security_issue.get('issue')
            resource_id = security_issue.get('resource')
            
            if issue_type == 'Unencrypted S3 bucket':
                return self._add_s3_encryption(template, resource_id)
            elif issue_type == 'Overly permissive security group':
                return self._restrict_security_group(template, resource_id)
            else:
                return {
                    'applied': False,
                    'reason': f'No handler for security issue: {issue_type}'
                }
                
        except Exception as e:
            return {
                'applied': False,
                'reason': str(e)
            }
    
    def _add_s3_encryption(self, template: Dict[str, Any], resource_id: str) -> Dict[str, Any]:
        """Add encryption to S3 bucket"""
        try:
            if resource_id not in template.get('Resources', {}):
                return {
                    'applied': False,
                    'reason': f'Resource {resource_id} not found'
                }
            
            resource = template['Resources'][resource_id]
            properties = resource.get('Properties', {})
            
            encryption_config = {
                'ServerSideEncryptionConfiguration': [{
                    'ServerSideEncryptionByDefault': {
                        'SSEAlgorithm': 'AES256'
                    }
                }]
            }
            
            properties['BucketEncryption'] = encryption_config
            
            fix = TemplateFix(
                fix_id=str(uuid.uuid4()),
                resource_id=resource_id,
                fix_type='ADD_ENCRYPTION',
                description=f'Added encryption to S3 bucket {resource_id}',
                original_value=None,
                new_value=encryption_config,
                confidence='HIGH'
            )
            
            return {
                'applied': True,
                'fix': fix
            }
            
        except Exception as e:
            return {
                'applied': False,
                'reason': str(e)
            }
    
    def _apply_best_practices(self, template: Dict[str, Any], analysis: Dict[str, Any]) -> List[TemplateFix]:
        """Apply AWS best practices to template"""
        fixes = []
        
        try:
            # Add tags to resources
            resources = template.get('Resources', {})
            for resource_id, resource in resources.items():
                resource_type = resource.get('Type')
                properties = resource.get('Properties', {})
                
                if self._resource_supports_tags(resource_type) and 'Tags' not in properties:
                    default_tags = [
                        {'Key': 'Environment', 'Value': 'Development'},
                        {'Key': 'ManagedBy', 'Value': 'CloudFormation'}
                    ]
                    
                    properties['Tags'] = default_tags
                    
                    fix = TemplateFix(
                        fix_id=str(uuid.uuid4()),
                        resource_id=resource_id,
                        fix_type='ADD_TAGS',
                        description=f'Added default tags to {resource_id}',
                        original_value=None,
                        new_value=default_tags,
                        confidence='MEDIUM'
                    )
                    fixes.append(fix)
            
        except Exception as e:
            logger.exception(f"Error applying best practices: {e}")
        
        return fixes
    
    def _get_failure_fix_strategy(self, failure_reason: str, resource_id: str) -> Optional[Dict[str, Any]]:
        """Get fix strategy for specific failure reason"""
        failure_patterns = {
            'already exists': {
                'type': 'MODIFY_PROPERTY',
                'property_path': 'BucketName',
                'property_value': f"{{resource_id}}-{{random_suffix}}",
                'confidence': 'HIGH'
            },
            'invalid bucket name': {
                'type': 'MODIFY_PROPERTY',
                'property_path': 'BucketName',
                'property_value': f"{resource_id.lower()}-{uuid.uuid4().hex[:8]}",
                'confidence': 'HIGH'
            },
            'access denied': {
                'type': 'ADD_RESOURCE',
                'resource_template': self._get_iam_policy_template(),
                'resource_name': f"{resource_id}Policy",
                'confidence': 'MEDIUM'
            }
        }
        
        for pattern, strategy in failure_patterns.items():
            if pattern.lower() in failure_reason.lower():
                return strategy
        
        return None
    
    def _resource_supports_tags(self, resource_type: str) -> bool:
        """Check if resource type supports tags"""
        taggable_resources = {
            'AWS::S3::Bucket',
            'AWS::Lambda::Function',
            'AWS::DynamoDB::Table',
            'AWS::IAM::Role',
            'AWS::EC2::Instance',
            'AWS::ApiGateway::RestApi',
            'AWS::RDS::DBInstance',
            'AWS::ECS::Service'
        }
        return resource_type in taggable_resources
    
    def _load_fix_strategies(self) -> Dict[str, Any]:
        """Load fix strategies for different issue types"""
        return {
            'MISSING_VERSION': {
                'type': 'ADD_TEMPLATE_SECTION',
                'property_path': 'AWSTemplateFormatVersion',
                'property_value': '2010-09-09',
                'confidence': 'HIGH'
            },
            'MISSING_PROPERTY': {
                'type': 'ADD_PROPERTY',
                'confidence': 'HIGH'
            },
            'INVALID_PROPERTY': {
                'type': 'MODIFY_PROPERTY',
                'confidence': 'MEDIUM'
            },
            'MISSING_TYPE': {
                'type': 'ADD_PROPERTY',
                'property_path': 'Type',
                'confidence': 'HIGH'
            }
        }
    
    def _add_template_section_fix(self, template: Dict[str, Any], issue: TemplateIssue, 
                                 strategy: Dict[str, Any]) -> Dict[str, Any]:
        """Add template-level section or property"""
        try:
            property_path = strategy.get('property_path')
            property_value = strategy.get('property_value')
            
            if property_path == 'AWSTemplateFormatVersion':
                template['AWSTemplateFormatVersion'] = property_value
                return {
                    'success': True,
                    'description': f'Added {property_path} to template',
                    'original_value': None,
                    'new_value': property_value
                }
            else:
                return {
                    'success': False,
                    'error': f'Unknown template section: {property_path}'
                }
                
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def _remove_property_fix(self, template: Dict[str, Any], issue: TemplateIssue, 
                           strategy: Dict[str, Any]) -> Dict[str, Any]:
        """Remove property from resource"""
        try:
            resource_id = issue.resource_id
            property_path = strategy.get('property_path')
            
            if resource_id not in template.get('Resources', {}):
                return {
                    'success': False,
                    'error': f'Resource {resource_id} not found'
                }
            
            resource = template['Resources'][resource_id]
            properties = resource.get('Properties', {})
            
            # Handle nested property paths
            path_parts = property_path.split('.')
            current = properties
            
            for part in path_parts[:-1]:
                if part not in current:
                    return {
                        'success': False,
                        'error': f'Property path {property_path} not found'
                    }
                current = current[part]
            
            if path_parts[-1] in current:
                original_value = current.pop(path_parts[-1])
                return {
                    'success': True,
                    'description': f'Removed {property_path} from {resource_id}',
                    'original_value': original_value,
                    'new_value': None
                }
            else:
                return {
                    'success': False,
                    'error': f'Property {path_parts[-1]} not found'
                }
                
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def _apply_failure_fix(self, template: Dict[str, Any], fix_strategy: Dict[str, Any], 
                          resource_id: str) -> Dict[str, Any]:
        """Apply fix for specific deployment failure"""
        try:
            strategy_type = fix_strategy.get('type')
            
            if strategy_type == 'MODIFY_PROPERTY':
                property_path = fix_strategy.get('property_path')
                property_value = fix_strategy.get('property_value')
                
                # Handle template variables in property value
                if isinstance(property_value, str):
                    property_value = property_value.replace('{resource_id}', resource_id)
                    property_value = property_value.replace('{random_suffix}', uuid.uuid4().hex[:8])
                
                # Create a mock issue for the fix
                mock_issue = TemplateIssue(
                    resource_id=resource_id,
                    issue_type='DEPLOYMENT_FAILURE',
                    severity='HIGH',
                    description='Deployment failure fix',
                    fix_suggestion='Auto-generated fix'
                )
                
                return self._modify_property_fix(template, mock_issue, {
                    'property_path': property_path,
                    'property_value': property_value
                })
            
            elif strategy_type == 'ADD_RESOURCE':
                resource_template = fix_strategy.get('resource_template')
                resource_name = fix_strategy.get('resource_name')
                
                mock_issue = TemplateIssue(
                    resource_id=resource_id,
                    issue_type='DEPLOYMENT_FAILURE',
                    severity='HIGH',
                    description='Deployment failure fix',
                    fix_suggestion='Auto-generated fix'
                )
                
                return self._add_resource_fix(template, mock_issue, {
                    'resource_template': resource_template,
                    'resource_name': resource_name
                })
            
            else:
                return {
                    'applied': False,
                    'reason': f'Unknown failure fix strategy: {strategy_type}'
                }
                
        except Exception as e:
            return {
                'applied': False,
                'reason': str(e)
            }
    
    def _add_api_gateway_methods(self, template: Dict[str, Any]) -> Dict[str, Any]:
        """Add basic API Gateway methods to template"""
        try:
            # Find API Gateway RestApi resources
            api_resources = []
            for resource_id, resource in template.get('Resources', {}).items():
                if resource.get('Type') == 'AWS::ApiGateway::RestApi':
                    api_resources.append(resource_id)
            
            if not api_resources:
                return {
                    'applied': False,
                    'reason': 'No API Gateway RestApi resources found'
                }
            
            # Add a basic method for the first API
            api_id = api_resources[0]
            method_name = f"{api_id}Method{uuid.uuid4().hex[:8]}"
            
            method_resource = {
                'Type': 'AWS::ApiGateway::Method',
                'Properties': {
                    'RestApiId': {'Ref': api_id},
                    'ResourceId': {'Fn::GetAtt': [api_id, 'RootResourceId']},
                    'HttpMethod': 'GET',
                    'AuthorizationType': 'NONE',
                    'Integration': {
                        'Type': 'MOCK',
                        'IntegrationResponses': [{
                            'StatusCode': '200'
                        }]
                    },
                    'MethodResponses': [{
                        'StatusCode': '200'
                    }]
                }
            }
            
            template['Resources'][method_name] = method_resource
            
            fix = TemplateFix(
                fix_id=str(uuid.uuid4()),
                resource_id=method_name,
                fix_type='ADD_MISSING_COMPONENT',
                description=f'Added API Gateway method {method_name}',
                original_value=None,
                new_value=method_resource,
                confidence='MEDIUM'
            )
            
            return {
                'applied': True,
                'fix': fix
            }
            
        except Exception as e:
            return {
                'applied': False,
                'reason': str(e)
            }
    
    def _restrict_security_group(self, template: Dict[str, Any], resource_id: str) -> Dict[str, Any]:
        """Restrict overly permissive security group rules"""
        try:
            if resource_id not in template.get('Resources', {}):
                return {
                    'applied': False,
                    'reason': f'Resource {resource_id} not found'
                }
            
            resource = template['Resources'][resource_id]
            properties = resource.get('Properties', {})
            
            # Restrict ingress rules
            ingress_rules = properties.get('SecurityGroupIngress', [])
            modified = False
            
            for rule in ingress_rules:
                if rule.get('CidrIp') == '0.0.0.0/0':
                    # Change to more restrictive CIDR
                    rule['CidrIp'] = '10.0.0.0/8'  # Private network range
                    modified = True
            
            if modified:
                fix = TemplateFix(
                    fix_id=str(uuid.uuid4()),
                    resource_id=resource_id,
                    fix_type='RESTRICT_SECURITY_GROUP',
                    description=f'Restricted security group {resource_id} to private network',
                    original_value='0.0.0.0/0',
                    new_value='10.0.0.0/8',
                    confidence='MEDIUM'
                )
                
                return {
                    'applied': True,
                    'fix': fix
                }
            else:
                return {
                    'applied': False,
                    'reason': 'No overly permissive rules found'
                }
                
        except Exception as e:
            return {
                'applied': False,
                'reason': str(e)
            }
    
    def _get_iam_policy_template(self) -> Dict[str, Any]:
        """Get template for IAM policy"""
        return {
            'Type': 'AWS::IAM::Policy',
            'Properties': {
                'PolicyName': 'DefaultPolicy',
                'PolicyDocument': {
                    'Version': '2012-10-17',
                    'Statement': [{
                        'Effect': 'Allow',
                        'Action': [
                            'logs:CreateLogGroup',
                            'logs:CreateLogStream',
                            'logs:PutLogEvents'
                        ],
                        'Resource': '*'
                    }]
                },
                'Roles': []
            }
        }
    
    def _load_best_practices(self) -> Dict[str, Any]:
        """Load AWS best practices configurations"""
        return {
            'default_tags': [
                {'Key': 'Environment', 'Value': 'Development'},
                {'Key': 'ManagedBy', 'Value': 'CloudFormation'},
                {'Key': 'CreatedBy', 'Value': 'EnhancedCFNMCP'}
            ],
            's3_encryption': {
                'ServerSideEncryptionConfiguration': [{
                    'ServerSideEncryptionByDefault': {
                        'SSEAlgorithm': 'AES256'
                    }
                }]
            }
        }
        """Load AWS best practices configurations"""
        return {
            'default_tags': [
                {'Key': 'Environment', 'Value': 'Development'},
                {'Key': 'ManagedBy', 'Value': 'CloudFormation'},
                {'Key': 'CreatedBy', 'Value': 'EnhancedCFNMCP'}
            ],
            's3_encryption': {
                'ServerSideEncryptionConfiguration': [{
                    'ServerSideEncryptionByDefault': {
                        'SSEAlgorithm': 'AES256'
                    }
                }]
            }
        }
