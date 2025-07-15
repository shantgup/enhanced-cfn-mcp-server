"""
Enhanced CloudFormation Template Analysis Module

This module provides deep analysis of CloudFormation templates to identify
issues, validate configurations, and understand resource relationships.
"""

import json
from typing import Dict, List, Any, Optional, Set, Tuple
try:
    import yaml
except ImportError:
    yaml = None
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)

@dataclass
class TemplateIssue:
    """Represents an issue found in a CloudFormation template"""
    resource_id: str
    issue_type: str
    severity: str  # HIGH, MEDIUM, LOW
    description: str
    fix_suggestion: str
    property_path: Optional[str] = None

@dataclass
class ResourceDependency:
    """Represents a dependency between resources"""
    source: str
    target: str
    dependency_type: str  # REF, GET_ATT, DEPENDS_ON
    property_path: str

class TemplateAnalyzer:
    """Analyzes CloudFormation templates for issues and improvements"""
    
    def __init__(self):
        self.aws_resource_schemas = {}  # Cache for AWS resource schemas
        self.common_fixes = self._load_common_fixes()
    
    def analyze_template(self, template: Dict[str, Any]) -> Dict[str, Any]:
        """
        Comprehensive template analysis
        
        Args:
            template: CloudFormation template as dictionary
            
        Returns:
            Analysis results with issues, dependencies, and recommendations
        """
        try:
            analysis = {
                'template_valid': True,
                'issues': [],
                'dependencies': [],
                'resource_analysis': {},
                'missing_components': [],
                'security_issues': [],
                'best_practice_violations': [],
                'recommendations': []
            }
            
            # Basic template structure validation
            structure_issues = self._validate_template_structure(template)
            analysis['issues'].extend(structure_issues)
            
            # Analyze each resource
            resources = template.get('Resources', {})
            for resource_id, resource_def in resources.items():
                resource_analysis = self._analyze_resource(resource_id, resource_def, template)
                analysis['resource_analysis'][resource_id] = resource_analysis
                analysis['issues'].extend(resource_analysis.get('issues', []))
            
            # Build dependency graph
            analysis['dependencies'] = self._build_dependency_graph(template)
            
            # Check for circular dependencies
            circular_deps = self._detect_circular_dependencies(analysis['dependencies'])
            if circular_deps:
                analysis['issues'].append(TemplateIssue(
                    resource_id='TEMPLATE',
                    issue_type='CIRCULAR_DEPENDENCY',
                    severity='HIGH',
                    description=f'Circular dependencies detected: {circular_deps}',
                    fix_suggestion='Remove circular references between resources'
                ))
            
            # Identify missing components
            analysis['missing_components'] = self._identify_missing_components(template)
            
            # Security analysis
            analysis['security_issues'] = self._analyze_security(template)
            
            # Best practices check
            analysis['best_practice_violations'] = self._check_best_practices(template)
            
            # Generate recommendations
            analysis['recommendations'] = self._generate_recommendations(analysis)
            
            return analysis
            
        except Exception as e:
            logger.exception(f"Error analyzing template: {e}")
            return {
                'template_valid': False,
                'error': str(e),
                'issues': [],
                'dependencies': [],
                'resource_analysis': {}
            }
    
    def correlate_with_stack_events(self, template_analysis: Dict, stack_events: List[Dict]) -> Dict[str, Any]:
        """
        Correlate template issues with actual stack deployment failures
        
        Args:
            template_analysis: Results from analyze_template
            stack_events: CloudFormation stack events
            
        Returns:
            Enhanced analysis with event correlation
        """
        try:
            correlation = {
                'correlated_issues': [],
                'root_cause_analysis': [],
                'fix_priority': []
            }
            
            # Find failed events
            failed_events = [
                event for event in stack_events 
                if event.get('ResourceStatus', '').endswith('_FAILED')
            ]
            
            for event in failed_events:
                resource_id = event.get('LogicalResourceId')
                status_reason = event.get('ResourceStatusReason', '')
                
                # Find matching template issues
                matching_issues = [
                    issue for issue in template_analysis.get('issues', [])
                    if issue.resource_id == resource_id
                ]
                
                # Analyze the failure reason
                failure_analysis = self._analyze_failure_reason(status_reason, resource_id, template_analysis)
                
                correlation['correlated_issues'].append({
                    'resource_id': resource_id,
                    'stack_event': event,
                    'template_issues': matching_issues,
                    'failure_analysis': failure_analysis,
                    'suggested_fixes': self._suggest_fixes_for_failure(failure_analysis)
                })
            
            # Prioritize fixes based on failure impact
            correlation['fix_priority'] = self._prioritize_fixes(correlation['correlated_issues'])
            
            return correlation
            
        except Exception as e:
            logger.exception(f"Error correlating template with stack events: {e}")
            return {'error': str(e)}
    
    def _validate_template_structure(self, template: Dict[str, Any]) -> List[TemplateIssue]:
        """Validate basic template structure"""
        issues = []
        
        # Check required sections
        if 'Resources' not in template:
            issues.append(TemplateIssue(
                resource_id='TEMPLATE',
                issue_type='MISSING_SECTION',
                severity='HIGH',
                description='Template missing Resources section',
                fix_suggestion='Add Resources section with at least one resource'
            ))
        
        # Check AWSTemplateFormatVersion
        if 'AWSTemplateFormatVersion' not in template:
            issues.append(TemplateIssue(
                resource_id='TEMPLATE',
                issue_type='MISSING_VERSION',
                severity='LOW',
                description='Template missing AWSTemplateFormatVersion',
                fix_suggestion='Add AWSTemplateFormatVersion: "2010-09-09"'
            ))
        
        # Check for empty resources
        resources = template.get('Resources', {})
        if not resources:
            issues.append(TemplateIssue(
                resource_id='TEMPLATE',
                issue_type='EMPTY_RESOURCES',
                severity='HIGH',
                description='Template has no resources defined',
                fix_suggestion='Add at least one AWS resource to the template'
            ))
        
        return issues
    
    def _analyze_resource(self, resource_id: str, resource_def: Dict[str, Any], template: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze individual resource for issues"""
        analysis = {
            'resource_type': resource_def.get('Type'),
            'issues': [],
            'missing_properties': [],
            'invalid_properties': [],
            'security_concerns': []
        }
        
        resource_type = resource_def.get('Type')
        properties = resource_def.get('Properties', {})
        
        # Check for missing Type
        if not resource_type:
            analysis['issues'].append(TemplateIssue(
                resource_id=resource_id,
                issue_type='MISSING_TYPE',
                severity='HIGH',
                description='Resource missing Type property',
                fix_suggestion='Add Type property with valid AWS resource type'
            ))
            return analysis
        
        # Validate against AWS resource schema (if available)
        schema_issues = self._validate_against_schema(resource_id, resource_type, properties)
        analysis['issues'].extend(schema_issues)
        
        # Check for common resource-specific issues
        resource_issues = self._check_resource_specific_issues(resource_id, resource_type, properties, template)
        analysis['issues'].extend(resource_issues)
        
        return analysis
    
    def _build_dependency_graph(self, template: Dict[str, Any]) -> List[ResourceDependency]:
        """Build resource dependency graph"""
        dependencies = []
        resources = template.get('Resources', {})
        
        for resource_id, resource_def in resources.items():
            # Check DependsOn
            depends_on = resource_def.get('DependsOn', [])
            if isinstance(depends_on, str):
                depends_on = [depends_on]
            
            for dep in depends_on:
                dependencies.append(ResourceDependency(
                    source=resource_id,
                    target=dep,
                    dependency_type='DEPENDS_ON',
                    property_path='DependsOn'
                ))
            
            # Check Ref and GetAtt in properties
            properties = resource_def.get('Properties', {})
            ref_deps = self._find_references(resource_id, properties)
            dependencies.extend(ref_deps)
        
        return dependencies
    
    def _find_references(self, resource_id: str, obj: Any, path: str = '') -> List[ResourceDependency]:
        """Recursively find Ref and GetAtt references"""
        dependencies = []
        
        if isinstance(obj, dict):
            if 'Ref' in obj:
                ref_target = obj['Ref']
                if ref_target not in ['AWS::AccountId', 'AWS::Region', 'AWS::StackId', 'AWS::StackName']:
                    dependencies.append(ResourceDependency(
                        source=resource_id,
                        target=ref_target,
                        dependency_type='REF',
                        property_path=path
                    ))
            
            elif 'Fn::GetAtt' in obj:
                get_att = obj['Fn::GetAtt']
                if isinstance(get_att, list) and len(get_att) > 0:
                    target = get_att[0]
                    dependencies.append(ResourceDependency(
                        source=resource_id,
                        target=target,
                        dependency_type='GET_ATT',
                        property_path=path
                    ))
            
            else:
                for key, value in obj.items():
                    new_path = f"{path}.{key}" if path else key
                    dependencies.extend(self._find_references(resource_id, value, new_path))
        
        elif isinstance(obj, list):
            for i, item in enumerate(obj):
                new_path = f"{path}[{i}]" if path else f"[{i}]"
                dependencies.extend(self._find_references(resource_id, item, new_path))
        
        return dependencies
    
    def _detect_circular_dependencies(self, dependencies: List[ResourceDependency]) -> List[str]:
        """Detect circular dependencies in the dependency graph"""
        # Build adjacency list
        graph = {}
        for dep in dependencies:
            if dep.source not in graph:
                graph[dep.source] = []
            graph[dep.source].append(dep.target)
        
        # DFS to detect cycles
        visited = set()
        rec_stack = set()
        cycles = []
        
        def dfs(node, path):
            if node in rec_stack:
                # Found a cycle
                cycle_start = path.index(node)
                cycle = path[cycle_start:] + [node]
                cycles.append(' -> '.join(cycle))
                return True
            
            if node in visited:
                return False
            
            visited.add(node)
            rec_stack.add(node)
            path.append(node)
            
            for neighbor in graph.get(node, []):
                if dfs(neighbor, path):
                    return True
            
            rec_stack.remove(node)
            path.pop()
            return False
        
        for node in graph:
            if node not in visited:
                dfs(node, [])
        
        return cycles
    
    def _identify_missing_components(self, template: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Identify missing components based on resource patterns"""
        missing = []
        resources = template.get('Resources', {})
        resource_types = [res.get('Type') for res in resources.values()]
        
        # Check for common missing components
        if 'AWS::ApiGateway::RestApi' in resource_types:
            if not any('AWS::ApiGateway::Method' in rt for rt in resource_types):
                missing.append({
                    'component': 'API Gateway Methods',
                    'severity': 'HIGH',
                    'description': 'API Gateway RestApi found but no Methods defined',
                    'fix_suggestion': 'Add AWS::ApiGateway::Method resources'
                })
        
        if 'AWS::Lambda::Function' in resource_types:
            if not any('AWS::IAM::Role' in rt for rt in resource_types):
                missing.append({
                    'component': 'Lambda Execution Role',
                    'severity': 'HIGH',
                    'description': 'Lambda function found but no execution role',
                    'fix_suggestion': 'Add AWS::IAM::Role for Lambda execution'
                })
        
        return missing
    
    def _analyze_security(self, template: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Analyze template for security issues"""
        security_issues = []
        resources = template.get('Resources', {})
        
        for resource_id, resource_def in resources.items():
            resource_type = resource_def.get('Type')
            properties = resource_def.get('Properties', {})
            
            # Check S3 bucket security
            if resource_type == 'AWS::S3::Bucket':
                if 'BucketEncryption' not in properties:
                    security_issues.append({
                        'resource': resource_id,
                        'issue': 'Unencrypted S3 bucket',
                        'severity': 'HIGH',
                        'description': 'S3 bucket does not have encryption enabled',
                        'fix_suggestion': 'Add BucketEncryption configuration'
                    })
            
            # Check security group rules
            elif resource_type == 'AWS::EC2::SecurityGroup':
                ingress_rules = properties.get('SecurityGroupIngress', [])
                for rule in ingress_rules:
                    if rule.get('CidrIp') == '0.0.0.0/0':
                        security_issues.append({
                            'resource': resource_id,
                            'issue': 'Overly permissive security group',
                            'severity': 'MEDIUM',
                            'description': 'Security group allows access from anywhere',
                            'fix_suggestion': 'Restrict CidrIp to specific IP ranges'
                        })
        
        return security_issues
    
    def _check_best_practices(self, template: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Check for AWS best practices violations"""
        violations = []
        
        # Check for missing tags
        resources = template.get('Resources', {})
        untagged_resources = []
        
        for resource_id, resource_def in resources.items():
            properties = resource_def.get('Properties', {})
            if 'Tags' not in properties and self._resource_supports_tags(resource_def.get('Type')):
                untagged_resources.append(resource_id)
        
        if untagged_resources:
            violations.append({
                'violation': 'Missing resource tags',
                'severity': 'LOW',
                'resources': untagged_resources,
                'description': 'Resources should be tagged for cost tracking and governance',
                'fix_suggestion': 'Add Tags property to resources'
            })
        
        return violations
    
    def _generate_recommendations(self, analysis: Dict[str, Any]) -> List[str]:
        """Generate actionable recommendations based on analysis"""
        recommendations = []
        
        high_severity_issues = [
            issue for issue in analysis.get('issues', [])
            if issue.severity == 'HIGH'
        ]
        
        if high_severity_issues:
            recommendations.append(f"Fix {len(high_severity_issues)} high-severity issues first")
        
        if analysis.get('security_issues'):
            recommendations.append("Address security vulnerabilities before deployment")
        
        if analysis.get('missing_components'):
            recommendations.append("Add missing components for complete functionality")
        
        return recommendations
    
    def _analyze_failure_reason(self, status_reason: str, resource_id: str, template_analysis: Dict) -> Dict[str, Any]:
        """Analyze CloudFormation failure reason"""
        analysis = {
            'failure_type': 'UNKNOWN',
            'root_cause': status_reason,
            'template_related': False,
            'fix_confidence': 'LOW'
        }
        
        # Pattern matching for common failures
        if 'already exists' in status_reason.lower():
            analysis['failure_type'] = 'RESOURCE_ALREADY_EXISTS'
            analysis['template_related'] = True
            analysis['fix_confidence'] = 'HIGH'
        
        elif 'invalid' in status_reason.lower() or 'validation' in status_reason.lower():
            analysis['failure_type'] = 'VALIDATION_ERROR'
            analysis['template_related'] = True
            analysis['fix_confidence'] = 'HIGH'
        
        elif 'permission' in status_reason.lower() or 'access denied' in status_reason.lower():
            analysis['failure_type'] = 'PERMISSION_ERROR'
            analysis['template_related'] = False
            analysis['fix_confidence'] = 'MEDIUM'
        
        return analysis
    
    def _suggest_fixes_for_failure(self, failure_analysis: Dict) -> List[str]:
        """Suggest specific fixes based on failure analysis"""
        fixes = []
        
        failure_type = failure_analysis.get('failure_type')
        
        if failure_type == 'RESOURCE_ALREADY_EXISTS':
            fixes.append("Use unique resource names or add random suffix")
            fixes.append("Check if resource should be imported instead of created")
        
        elif failure_type == 'VALIDATION_ERROR':
            fixes.append("Validate resource properties against AWS documentation")
            fixes.append("Check for missing required properties")
        
        elif failure_type == 'PERMISSION_ERROR':
            fixes.append("Add required IAM permissions to deployment role")
            fixes.append("Check resource-based policies")
        
        return fixes
    
    def _prioritize_fixes(self, correlated_issues: List[Dict]) -> List[Dict]:
        """Prioritize fixes based on impact and confidence"""
        priority_order = []
        
        for issue in correlated_issues:
            failure_analysis = issue.get('failure_analysis', {})
            confidence = failure_analysis.get('fix_confidence', 'LOW')
            template_related = failure_analysis.get('template_related', False)
            
            priority_score = 0
            if confidence == 'HIGH':
                priority_score += 3
            elif confidence == 'MEDIUM':
                priority_score += 2
            else:
                priority_score += 1
            
            if template_related:
                priority_score += 2
            
            priority_order.append({
                'issue': issue,
                'priority_score': priority_score
            })
        
        # Sort by priority score (highest first)
        priority_order.sort(key=lambda x: x['priority_score'], reverse=True)
        
        return [item['issue'] for item in priority_order]
    
    def _validate_against_schema(self, resource_id: str, resource_type: str, properties: Dict) -> List[TemplateIssue]:
        """Validate resource properties against AWS schema"""
        # This would integrate with AWS CloudFormation resource schemas
        # For now, return basic validation
        issues = []
        
        # Basic validation for common resource types
        if resource_type == 'AWS::S3::Bucket':
            if 'BucketName' in properties:
                bucket_name = properties['BucketName']
                if not isinstance(bucket_name, str) or len(bucket_name) < 3:
                    issues.append(TemplateIssue(
                        resource_id=resource_id,
                        issue_type='INVALID_PROPERTY',
                        severity='HIGH',
                        description='Invalid bucket name',
                        fix_suggestion='Bucket name must be at least 3 characters',
                        property_path='Properties.BucketName'
                    ))
        
        return issues
    
    def _check_resource_specific_issues(self, resource_id: str, resource_type: str, properties: Dict, template: Dict) -> List[TemplateIssue]:
        """Check for resource-specific common issues"""
        issues = []
        
        # Lambda function checks
        if resource_type == 'AWS::Lambda::Function':
            if 'Role' not in properties:
                issues.append(TemplateIssue(
                    resource_id=resource_id,
                    issue_type='MISSING_PROPERTY',
                    severity='HIGH',
                    description='Lambda function missing execution role',
                    fix_suggestion='Add Role property with IAM role ARN',
                    property_path='Properties.Role'
                ))
        
        return issues
    
    def _resource_supports_tags(self, resource_type: str) -> bool:
        """Check if resource type supports tags"""
        taggable_resources = {
            'AWS::S3::Bucket',
            'AWS::Lambda::Function',
            'AWS::DynamoDB::Table',
            'AWS::IAM::Role',
            'AWS::EC2::Instance',
            'AWS::ApiGateway::RestApi'
        }
        return resource_type in taggable_resources
    
    def _load_common_fixes(self) -> Dict[str, Any]:
        """Load common fixes for template issues"""
        return {
            'missing_execution_role': {
                'resource_type': 'AWS::IAM::Role',
                'properties': {
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
        }
