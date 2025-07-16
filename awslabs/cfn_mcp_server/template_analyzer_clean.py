#!/usr/bin/env python3
"""
Clean Template Analysis Prompt Enhancement Module

This module transforms basic template analysis requests into expert-level prompts for Claude.
It provides comprehensive CloudFormation template analysis with security, performance, 
compliance, and architectural best practices guidance.
"""

import json
import yaml
import re
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime


class TemplateAnalyzer:
    """
    Clean template analysis prompt enhancer that transforms basic analysis requests
    into comprehensive expert-level prompts for Claude.
    """
    
    def __init__(self):
        self.security_patterns = {
            'hardcoded_secrets': [
                r'password.*["\'].*["\']',
                r'secret.*["\'].*["\']',
                r'key.*["\'].*["\']',
                r'token.*["\'].*["\']'
            ],
            'overly_permissive': [
                r'0\.0\.0\.0/0',
                r'\*',
                r'Action.*\*'
            ],
            'unencrypted_storage': [
                r'StorageEncrypted.*false',
                r'Encrypted.*false'
            ]
        }
        
        self.compliance_indicators = {
            'hipaa': ['phi', 'hipaa', 'healthcare', 'medical', 'patient'],
            'pci': ['pci', 'payment', 'card', 'transaction', 'financial'],
            'sox': ['sox', 'sarbanes', 'financial', 'audit', 'compliance'],
            'gdpr': ['gdpr', 'privacy', 'personal', 'data protection']
        }
        
        self.architecture_patterns = {
            'microservices': ['ecs', 'eks', 'fargate', 'service', 'container', 'api gateway'],
            'serverless': ['lambda', 'api gateway', 'dynamodb', 'step functions'],
            'web_application': ['alb', 'ec2', 'rds', 'cloudfront', 'route53'],
            'data_pipeline': ['kinesis', 'glue', 'emr', 'redshift', 'athena'],
            'machine_learning': ['sagemaker', 'ml', 'model', 'training', 'inference']
        }

    def generate_enhanced_prompt(
        self,
        template_content: str,
        region: Optional[str] = None,
        analysis_focus: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Generate comprehensive expert-level template analysis prompt for Claude.
        
        Args:
            template_content: CloudFormation template content (JSON or YAML)
            region: AWS region for context
            analysis_focus: Specific focus area (security, performance, compliance, architecture)
            
        Returns:
            Dictionary containing expert prompt and analysis context
        """
        try:
            # Parse template
            template_data = self._parse_template(template_content)
            if not template_data:
                return self._generate_parsing_error_prompt(template_content)
            
            # Analyze template structure
            analysis = self._analyze_template_structure(template_data)
            
            # Detect patterns and issues
            security_issues = self._detect_security_issues(template_content, template_data)
            compliance_requirements = self._detect_compliance_requirements(template_content, template_data)
            architecture_pattern = self._detect_architecture_pattern(template_data)
            performance_issues = self._detect_performance_issues(template_data)
            
            # Generate expert prompt
            expert_prompt = self._build_expert_analysis_prompt(
                template_data=template_data,
                analysis=analysis,
                security_issues=security_issues,
                compliance_requirements=compliance_requirements,
                architecture_pattern=architecture_pattern,
                performance_issues=performance_issues,
                region=region,
                analysis_focus=analysis_focus
            )
            
            return {
                'expert_prompt_for_claude': expert_prompt,
                'template_analysis': analysis,
                'security_assessment': security_issues,
                'compliance_requirements': compliance_requirements,
                'architecture_pattern': architecture_pattern,
                'performance_assessment': performance_issues,
                'analysis_workflow': self._generate_analysis_workflow(analysis_focus),
                'investigation_commands': self._generate_investigation_commands(template_data, region),
                'best_practices_checklist': self._generate_best_practices_checklist(
                    security_issues, compliance_requirements, architecture_pattern
                ),
                'remediation_guidance': self._generate_remediation_guidance(
                    security_issues, performance_issues
                ),
                'validation_steps': self._generate_validation_steps(),
                'region': region or 'us-east-1',
                'timestamp': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f"Template analysis failed: {str(e)}",
                'expert_prompt_for_claude': self._generate_error_analysis_prompt(str(e), template_content)
            }

    def _parse_template(self, template_content: str) -> Optional[Dict[str, Any]]:
        """Parse CloudFormation template from JSON or YAML using enhanced parser."""
        try:
            from awslabs.cfn_mcp_server.cloudformation_yaml import parse_cloudformation_template
            print(f"DEBUG: Attempting to parse template with enhanced parser")
            result = parse_cloudformation_template(template_content)
            print(f"DEBUG: Successfully parsed template with {len(result.get('Resources', {}))} resources")
            return result
        except Exception as e:
            print(f"DEBUG: Enhanced parser failed with error: {e}")
            return None

    def _analyze_template_structure(self, template_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze basic template structure and components."""
        resources = template_data.get('Resources', {})
        parameters = template_data.get('Parameters', {})
        outputs = template_data.get('Outputs', {})
        conditions = template_data.get('Conditions', {})
        
        # Resource analysis
        resource_types = {}
        for resource_name, resource_config in resources.items():
            resource_type = resource_config.get('Type', 'Unknown')
            if resource_type not in resource_types:
                resource_types[resource_type] = []
            resource_types[resource_type].append(resource_name)
        
        # Dependency analysis
        dependencies = self._analyze_dependencies(resources)
        
        return {
            'total_resources': len(resources),
            'resource_types': resource_types,
            'parameters_count': len(parameters),
            'outputs_count': len(outputs),
            'conditions_count': len(conditions),
            'dependencies': dependencies,
            'complexity_score': self._calculate_complexity_score(template_data)
        }

    def _detect_security_issues(self, template_content: str, template_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Detect security issues in the template."""
        issues = []
        
        # Check for hardcoded secrets
        for pattern_name, patterns in self.security_patterns.items():
            for pattern in patterns:
                matches = re.findall(pattern, template_content, re.IGNORECASE)
                if matches:
                    issues.append({
                        'type': pattern_name,
                        'severity': 'HIGH',
                        'description': f"Potential {pattern_name.replace('_', ' ')} detected",
                        'matches': len(matches),
                        'pattern': pattern
                    })
        
        # Check specific resource security configurations
        resources = template_data.get('Resources', {})
        for resource_name, resource_config in resources.items():
            resource_type = resource_config.get('Type', '')
            properties = resource_config.get('Properties', {})
            
            # S3 bucket security
            if resource_type == 'AWS::S3::Bucket':
                if not properties.get('PublicAccessBlockConfiguration'):
                    issues.append({
                        'type': 'missing_public_access_block',
                        'severity': 'HIGH',
                        'resource': resource_name,
                        'description': 'S3 bucket missing PublicAccessBlockConfiguration'
                    })
                
                if not properties.get('BucketEncryption'):
                    issues.append({
                        'type': 'unencrypted_storage',
                        'severity': 'HIGH',
                        'resource': resource_name,
                        'description': 'S3 bucket not encrypted'
                    })
            
            # RDS security
            elif resource_type == 'AWS::RDS::DBInstance':
                if not properties.get('StorageEncrypted', False):
                    issues.append({
                        'type': 'unencrypted_storage',
                        'severity': 'HIGH',
                        'resource': resource_name,
                        'description': 'RDS instance storage not encrypted'
                    })
        
        return issues

    def _detect_compliance_requirements(self, template_content: str, template_data: Dict[str, Any]) -> List[str]:
        """Detect compliance requirements based on template content."""
        detected_compliance = []
        
        content_lower = template_content.lower()
        for compliance_type, indicators in self.compliance_indicators.items():
            if any(indicator in content_lower for indicator in indicators):
                detected_compliance.append(compliance_type.upper())
        
        return detected_compliance

    def _detect_architecture_pattern(self, template_data: Dict[str, Any]) -> str:
        """Detect the primary architecture pattern."""
        resources = template_data.get('Resources', {})
        resource_types = [res.get('Type', '').lower() for res in resources.values()]
        
        pattern_scores = {}
        for pattern, indicators in self.architecture_patterns.items():
            score = sum(1 for indicator in indicators if any(indicator in rt for rt in resource_types))
            if score > 0:
                pattern_scores[pattern] = score
        
        if pattern_scores:
            return max(pattern_scores.items(), key=lambda x: x[1])[0]
        return 'general_infrastructure'

    def _detect_performance_issues(self, template_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Detect potential performance issues."""
        issues = []
        resources = template_data.get('Resources', {})
        
        for resource_name, resource_config in resources.items():
            resource_type = resource_config.get('Type', '')
            properties = resource_config.get('Properties', {})
            
            # RDS performance
            if resource_type == 'AWS::RDS::DBInstance':
                if properties.get('DBInstanceClass', '').startswith('db.t'):
                    issues.append({
                        'type': 'suboptimal_instance_type',
                        'severity': 'MEDIUM',
                        'resource': resource_name,
                        'description': 'Using burstable instance type for database'
                    })
            
            # Lambda performance
            elif resource_type == 'AWS::Lambda::Function':
                memory_size = properties.get('MemorySize', 128)
                if memory_size < 512:
                    issues.append({
                        'type': 'low_memory_allocation',
                        'severity': 'MEDIUM',
                        'resource': resource_name,
                        'description': f'Lambda function has low memory allocation: {memory_size}MB'
                    })
        
        return issues

    def _build_expert_analysis_prompt(
        self,
        template_data: Dict[str, Any],
        analysis: Dict[str, Any],
        security_issues: List[Dict[str, Any]],
        compliance_requirements: List[str],
        architecture_pattern: str,
        performance_issues: List[Dict[str, Any]],
        region: Optional[str],
        analysis_focus: Optional[str]
    ) -> str:
        """Build comprehensive expert analysis prompt for Claude."""
        
        focus_guidance = {
            'security': 'Focus primarily on security vulnerabilities, compliance gaps, and hardening recommendations.',
            'performance': 'Focus primarily on performance optimization, resource sizing, and efficiency improvements.',
            'compliance': 'Focus primarily on compliance requirements, audit trails, and regulatory adherence.',
            'architecture': 'Focus primarily on architectural patterns, best practices, and design improvements.',
            'cost': 'Focus primarily on cost optimization, resource efficiency, and budget considerations.'
        }
        
        prompt = f"""
You are an expert AWS Solutions Architect and CloudFormation specialist with deep expertise in infrastructure security, performance optimization, and compliance frameworks.

TEMPLATE ANALYSIS REQUEST:
- Architecture Pattern: {architecture_pattern}
- Total Resources: {analysis['total_resources']}
- Complexity Score: {analysis['complexity_score']}/10
- Region Context: {region or 'us-east-1'}
- Analysis Focus: {analysis_focus or 'comprehensive'}

{focus_guidance.get(analysis_focus, 'Provide comprehensive analysis covering security, performance, compliance, and architectural best practices.')}

TEMPLATE STRUCTURE ANALYSIS:
Resource Distribution:
"""
        
        for resource_type, resources in analysis['resource_types'].items():
            prompt += f"- {resource_type}: {len(resources)} instances\n"
        
        prompt += f"""
Template Components:
- Parameters: {analysis['parameters_count']}
- Outputs: {analysis['outputs_count']}
- Conditions: {analysis['conditions_count']}

SECURITY ASSESSMENT:
"""
        
        if security_issues:
            prompt += f"⚠️ {len(security_issues)} Security Issues Detected:\n"
            for issue in security_issues[:5]:  # Show top 5
                prompt += f"- {issue['severity']}: {issue['description']}\n"
        else:
            prompt += "✅ No obvious security issues detected in initial scan\n"
        
        if compliance_requirements:
            prompt += f"\n🔒 Compliance Requirements Detected: {', '.join(compliance_requirements)}\n"
        
        prompt += f"""

PERFORMANCE ASSESSMENT:
"""
        
        if performance_issues:
            prompt += f"⚠️ {len(performance_issues)} Performance Issues Detected:\n"
            for issue in performance_issues[:5]:  # Show top 5
                prompt += f"- {issue['severity']}: {issue['description']}\n"
        else:
            prompt += "✅ No obvious performance issues detected in initial scan\n"
        
        prompt += f"""

EXPERT ANALYSIS REQUIREMENTS:

1. **COMPREHENSIVE SECURITY REVIEW**
   - Analyze each resource for security best practices
   - Identify hardcoded secrets, overly permissive policies, and unencrypted data
   - Review IAM roles, security groups, and access patterns
   - Validate encryption at rest and in transit
   - Check for compliance with security frameworks

2. **ARCHITECTURAL ASSESSMENT**
   - Evaluate the overall architecture pattern and design
   - Identify single points of failure and resilience gaps
   - Review resource dependencies and potential circular references
   - Assess scalability and maintainability
   - Validate AWS Well-Architected Framework alignment

3. **PERFORMANCE OPTIMIZATION**
   - Review resource sizing and instance types
   - Identify performance bottlenecks and optimization opportunities
   - Evaluate auto-scaling configurations
   - Check monitoring and observability setup
   - Assess cost optimization opportunities

4. **COMPLIANCE VALIDATION**
   - Verify adherence to detected compliance requirements
   - Review audit logging and data retention policies
   - Validate access controls and segregation of duties
   - Check data protection and privacy measures

5. **OPERATIONAL EXCELLENCE**
   - Review deployment and rollback strategies
   - Evaluate monitoring, alerting, and observability
   - Check backup and disaster recovery configurations
   - Assess automation and infrastructure as code practices

DELIVERABLES REQUIRED:

1. **Executive Summary**: High-level findings and risk assessment
2. **Detailed Security Analysis**: Specific vulnerabilities and remediation steps
3. **Performance Recommendations**: Concrete optimization suggestions
4. **Compliance Gap Analysis**: Requirements vs. current implementation
5. **Architectural Improvements**: Design enhancements and best practices
6. **Implementation Roadmap**: Prioritized action items with timelines
7. **Monitoring Strategy**: Comprehensive observability recommendations

Please provide a thorough, expert-level analysis with specific, actionable recommendations for each identified issue. Include exact CloudFormation template modifications, AWS CLI commands for validation, and step-by-step implementation guidance.

Focus on production-ready solutions that follow AWS best practices and industry standards.
"""
        
        return prompt

    def _generate_analysis_workflow(self, analysis_focus: Optional[str]) -> List[str]:
        """Generate systematic analysis workflow steps."""
        base_workflow = [
            "Parse and validate template structure",
            "Identify resource types and dependencies",
            "Analyze security configurations and vulnerabilities",
            "Evaluate performance and cost optimization opportunities",
            "Check compliance requirements and gaps",
            "Review architectural patterns and best practices",
            "Generate prioritized remediation recommendations",
            "Create implementation roadmap with timelines",
            "Validate fixes and test deployment strategy"
        ]
        
        focus_workflows = {
            'security': [
                "Scan for hardcoded secrets and credentials",
                "Analyze IAM policies and permissions",
                "Review encryption configurations",
                "Check network security and access controls",
                "Validate compliance with security frameworks",
                "Generate security remediation plan"
            ],
            'performance': [
                "Analyze resource sizing and instance types",
                "Review auto-scaling configurations",
                "Check monitoring and observability setup",
                "Identify performance bottlenecks",
                "Evaluate cost optimization opportunities",
                "Generate performance improvement plan"
            ]
        }
        
        if analysis_focus and analysis_focus in focus_workflows:
            return focus_workflows[analysis_focus]
        
        return base_workflow

    def _generate_investigation_commands(self, template_data: Dict[str, Any], region: Optional[str]) -> List[str]:
        """Generate AWS CLI commands for deeper investigation."""
        commands = [
            f"aws cloudformation validate-template --template-body file://template.yaml --region {region or 'us-east-1'}",
            f"aws cloudformation estimate-template-cost --template-body file://template.yaml --region {region or 'us-east-1'}",
            "aws iam simulate-principal-policy --policy-source-arn <role-arn> --action-names <actions> --resource-arns <resources>",
            "aws config get-compliance-details-by-config-rule --config-rule-name <rule-name>",
            "aws trustedadvisor describe-checks --language en"
        ]
        
        # Add resource-specific commands
        resources = template_data.get('Resources', {})
        for resource_name, resource_config in resources.items():
            resource_type = resource_config.get('Type', '')
            
            if resource_type == 'AWS::S3::Bucket':
                commands.append(f"aws s3api get-bucket-encryption --bucket <bucket-name>")
                commands.append(f"aws s3api get-public-access-block --bucket <bucket-name>")
            elif resource_type == 'AWS::RDS::DBInstance':
                commands.append(f"aws rds describe-db-instances --db-instance-identifier <db-id>")
                commands.append(f"aws rds describe-db-snapshots --db-instance-identifier <db-id>")
        
        return commands

    def _generate_best_practices_checklist(
        self,
        security_issues: List[Dict[str, Any]],
        compliance_requirements: List[str],
        architecture_pattern: str
    ) -> List[str]:
        """Generate best practices checklist based on analysis."""
        checklist = [
            "✓ All resources have appropriate tags for governance",
            "✓ IAM roles follow least privilege principle",
            "✓ Encryption enabled for data at rest and in transit",
            "✓ CloudWatch monitoring and alarms configured",
            "✓ Backup and recovery procedures defined",
            "✓ Security groups restrict access appropriately",
            "✓ Cost optimization measures implemented",
            "✓ Resource naming follows consistent conventions",
            "✓ Template uses parameters for environment-specific values",
            "✓ Outputs defined for cross-stack references"
        ]
        
        # Add compliance-specific items
        if 'HIPAA' in compliance_requirements:
            checklist.extend([
                "✓ PHI data encryption verified (AES-256)",
                "✓ Audit logging comprehensive and tamper-proof",
                "✓ Access controls documented and role-based"
            ])
        
        if 'PCI' in compliance_requirements:
            checklist.extend([
                "✓ Payment data encryption and tokenization",
                "✓ Network segmentation for cardholder data",
                "✓ Regular security testing and monitoring"
            ])
        
        # Add architecture-specific items
        if architecture_pattern == 'microservices':
            checklist.extend([
                "✓ Service discovery configured",
                "✓ Inter-service communication secured",
                "✓ Container health checks enabled"
            ])
        
        return checklist

    def _generate_remediation_guidance(
        self,
        security_issues: List[Dict[str, Any]],
        performance_issues: List[Dict[str, Any]]
    ) -> Dict[str, List[str]]:
        """Generate specific remediation guidance."""
        guidance = {
            'immediate_actions': [],
            'template_modifications': [],
            'operational_changes': []
        }
        
        # Security remediations
        for issue in security_issues:
            if issue['type'] == 'hardcoded_secrets':
                guidance['immediate_actions'].append("Remove hardcoded secrets from template")
                guidance['template_modifications'].append("Use AWS Systems Manager Parameter Store or Secrets Manager")
            
            elif issue['type'] == 'unencrypted_storage':
                guidance['template_modifications'].append("Enable encryption for all storage resources")
                guidance['operational_changes'].append("Implement key rotation policies")
        
        # Performance remediations
        for issue in performance_issues:
            if issue['type'] == 'suboptimal_instance_type':
                guidance['template_modifications'].append("Upgrade to production-grade instance types")
                guidance['operational_changes'].append("Implement auto-scaling based on metrics")
        
        return guidance

    def _generate_validation_steps(self) -> List[str]:
        """Generate validation steps for template analysis."""
        return [
            "✓ Template syntax validation completed",
            "✓ Resource dependencies verified",
            "✓ Security configurations reviewed",
            "✓ Performance optimizations identified",
            "✓ Compliance requirements validated",
            "✓ Cost estimation performed",
            "✓ Best practices alignment confirmed",
            "✓ Remediation plan prioritized",
            "✓ Implementation roadmap created"
        ]

    def _analyze_dependencies(self, resources: Dict[str, Any]) -> Dict[str, List[str]]:
        """Analyze resource dependencies."""
        dependencies = {}
        
        for resource_name, resource_config in resources.items():
            deps = []
            # Simple dependency detection based on Ref and GetAtt
            resource_str = str(resource_config)
            for other_resource in resources.keys():
                if other_resource != resource_name and other_resource in resource_str:
                    deps.append(other_resource)
            dependencies[resource_name] = deps
        
        return dependencies

    def _calculate_complexity_score(self, template_data: Dict[str, Any]) -> int:
        """Calculate template complexity score (1-10)."""
        resources = len(template_data.get('Resources', {}))
        parameters = len(template_data.get('Parameters', {}))
        conditions = len(template_data.get('Conditions', {}))
        outputs = len(template_data.get('Outputs', {}))
        
        # Simple scoring algorithm
        score = min(10, (resources // 5) + (parameters // 3) + (conditions * 2) + (outputs // 2))
        return max(1, score)

    def _generate_parsing_error_prompt(self, template_content: str) -> Dict[str, Any]:
        """Generate prompt for template parsing errors."""
        return {
            'success': False,
            'error': 'Template parsing failed',
            'expert_prompt_for_claude': f"""
You are an expert CloudFormation template troubleshooter. The provided template could not be parsed as valid JSON or YAML.

TEMPLATE PARSING ERROR ANALYSIS:

Please analyze the following template content and identify:

1. **Syntax Errors**: JSON/YAML formatting issues
2. **Structure Problems**: Missing required sections or malformed structure
3. **Character Encoding Issues**: Invalid characters or encoding problems
4. **CloudFormation Function Issues**: Incorrect intrinsic function usage

TEMPLATE CONTENT TO ANALYZE:
```
{template_content[:1000]}{'...' if len(template_content) > 1000 else ''}
```

REQUIRED DELIVERABLES:
1. Specific syntax errors with line numbers
2. Corrected template structure
3. Validation commands to verify fixes
4. Best practices for template formatting

Please provide detailed, actionable guidance to resolve the parsing issues.
"""
        }

    def _generate_error_analysis_prompt(self, error: str, template_content: str) -> str:
        """Generate prompt for analysis errors."""
        return f"""
You are an expert CloudFormation troubleshooter. An error occurred during template analysis.

ERROR DETAILS: {error}

TEMPLATE CONTENT (first 500 chars):
```
{template_content[:500]}{'...' if len(template_content) > 500 else ''}
```

Please analyze the error and provide:
1. Root cause analysis
2. Specific remediation steps
3. Alternative analysis approaches
4. Prevention measures for similar issues

Focus on actionable solutions to resolve the analysis failure.
"""

    def create_comprehensive_analysis(self, template: Dict[str, Any], analysis_focus: str = "comprehensive") -> Dict[str, Any]:
        """
        Create a comprehensive analysis of the CloudFormation template.
        
        Args:
            template: The CloudFormation template to analyze
            analysis_focus: Focus area for analysis (security, performance, compliance, comprehensive)
            
        Returns:
            Dict containing comprehensive analysis with expert prompt
        """
        try:
            # Parse template and extract information
            resources = template.get('Resources', {})
            parameters = template.get('Parameters', {})
            outputs = template.get('Outputs', {})
            
            # Perform security analysis
            security_assessment = self._analyze_security_patterns(template)
            
            # Identify architecture patterns
            architecture_pattern = self._identify_architecture_pattern(resources)
            
            # Generate compliance requirements
            compliance_requirements = self._assess_compliance_requirements(template)
            
            # Create performance assessment
            performance_assessment = self._assess_performance_patterns(resources)
            
            # Generate best practices checklist
            best_practices_checklist = self._generate_best_practices_checklist(template)
            
            # Create remediation guidance
            remediation_guidance = self._generate_remediation_guidance(security_assessment, performance_assessment)
            
            # Generate expert prompt for Claude
            # Convert template dict back to string for generate_enhanced_prompt
            import json
            template_content_str = json.dumps(template, indent=2)
            expert_prompt = self.generate_enhanced_prompt(
                template_content=template_content_str,
                analysis_focus=analysis_focus
            )
            
            return {
                'expert_prompt_for_claude': expert_prompt,
                'template_analysis': {
                    'resource_count': len(resources),
                    'parameter_count': len(parameters),
                    'output_count': len(outputs),
                    'architecture_pattern': architecture_pattern
                },
                'security_assessment': security_assessment,
                'compliance_requirements': compliance_requirements,
                'architecture_pattern': architecture_pattern,
                'performance_assessment': performance_assessment,
                'analysis_workflow': self._create_analysis_workflow(),
                'investigation_commands': self._generate_investigation_commands(),
                'best_practices_checklist': best_practices_checklist,
                'remediation_guidance': remediation_guidance,
                'validation_steps': self._generate_validation_steps(),
                'region': 'us-east-1',  # Default region
                'timestamp': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            return {
                'expert_prompt_for_claude': f"Error analyzing template: {str(e)}. Please provide the template content for analysis.",
                'error': str(e),
                'timestamp': datetime.utcnow().isoformat()
            }
    
    def _analyze_security_patterns(self, template: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze template for security patterns and issues."""
        template_str = json.dumps(template)
        issues = []
        
        for pattern_type, patterns in self.security_patterns.items():
            for pattern in patterns:
                if re.search(pattern, template_str, re.IGNORECASE):
                    issues.append({
                        'type': pattern_type,
                        'pattern': pattern,
                        'severity': 'HIGH' if pattern_type == 'hardcoded_secrets' else 'MEDIUM'
                    })
        
        return {
            'issues': issues,
            'score': max(0, 100 - len(issues) * 10),
            'recommendations': self._get_security_recommendations(issues)
        }
    
    def _identify_architecture_pattern(self, resources: Dict[str, Any]) -> str:
        """Identify the architecture pattern from resources."""
        resource_types = [res.get('Type', '') for res in resources.values()]
        resource_str = ' '.join(resource_types).lower()
        
        for pattern, keywords in self.architecture_patterns.items():
            if any(keyword in resource_str for keyword in keywords):
                return pattern
        
        return 'custom'
    
    def _assess_compliance_requirements(self, template: Dict[str, Any]) -> List[str]:
        """Assess compliance requirements based on template content."""
        template_str = json.dumps(template).lower()
        requirements = []
        
        for compliance_type, indicators in self.compliance_indicators.items():
            if any(indicator in template_str for indicator in indicators):
                requirements.append(compliance_type.upper())
        
        return requirements
    
    def _assess_performance_patterns(self, resources: Dict[str, Any]) -> Dict[str, Any]:
        """Assess performance patterns in the template."""
        performance_issues = []
        recommendations = []
        
        for resource_name, resource in resources.items():
            resource_type = resource.get('Type', '')
            properties = resource.get('Properties', {})
            
            # Check for common performance issues
            if resource_type == 'AWS::RDS::DBInstance':
                if not properties.get('MultiAZ'):
                    performance_issues.append(f"{resource_name}: Consider enabling MultiAZ for high availability")
                    
            elif resource_type == 'AWS::Lambda::Function':
                memory = properties.get('MemorySize', 128)
                if memory < 256:
                    recommendations.append(f"{resource_name}: Consider increasing memory for better performance")
        
        return {
            'issues': performance_issues,
            'recommendations': recommendations,
            'score': max(0, 100 - len(performance_issues) * 15)
        }
    
    def _generate_best_practices_checklist(self, template: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate a best practices checklist for the template."""
        checklist = [
            {
                'category': 'Security',
                'items': [
                    'All storage resources have encryption enabled',
                    'IAM roles follow least privilege principle',
                    'No hardcoded secrets in template',
                    'Security groups have minimal required access'
                ]
            },
            {
                'category': 'Performance',
                'items': [
                    'Resources are right-sized for workload',
                    'Auto Scaling is configured where appropriate',
                    'Caching is implemented for frequently accessed data',
                    'Multi-AZ deployment for critical resources'
                ]
            },
            {
                'category': 'Cost Optimization',
                'items': [
                    'Lifecycle policies configured for storage',
                    'Reserved instances considered for predictable workloads',
                    'Unused resources are cleaned up',
                    'Resource tagging for cost allocation'
                ]
            }
        ]
        return checklist
    
    def _generate_remediation_guidance(self, security_assessment: Dict[str, Any], performance_assessment: Dict[str, Any]) -> List[str]:
        """Generate remediation guidance based on assessments."""
        guidance = []
        
        # Security remediation
        for issue in security_assessment.get('issues', []):
            if issue['type'] == 'hardcoded_secrets':
                guidance.append("Replace hardcoded secrets with AWS Secrets Manager or Parameter Store references")
            elif issue['type'] == 'overly_permissive':
                guidance.append("Restrict overly permissive security group rules and IAM policies")
            elif issue['type'] == 'unencrypted_storage':
                guidance.append("Enable encryption for all storage resources")
        
        # Performance remediation
        for issue in performance_assessment.get('issues', []):
            guidance.append(f"Performance: {issue}")
        
        return guidance
    
    def _create_analysis_workflow(self) -> List[str]:
        """Create analysis workflow steps."""
        return [
            "1. Parse and validate CloudFormation template syntax",
            "2. Identify all resources and their configurations",
            "3. Analyze security patterns and potential vulnerabilities",
            "4. Assess compliance requirements based on resource types",
            "5. Evaluate architecture patterns and best practices",
            "6. Generate recommendations and remediation guidance",
            "7. Create comprehensive analysis report"
        ]
    
    def _generate_investigation_commands(self) -> List[str]:
        """Generate investigation commands for further analysis."""
        return [
            "aws cloudformation validate-template --template-body file://template.yaml",
            "cfn-lint template.yaml",
            "aws cloudformation estimate-template-cost --template-body file://template.yaml",
            "aws cloudformation create-change-set --stack-name test-stack --template-body file://template.yaml --change-set-name analysis-changeset"
        ]
    
    def _generate_validation_steps(self) -> List[str]:
        """Generate validation steps for the template."""
        return [
            "Validate template syntax with AWS CLI",
            "Run security analysis with cfn-nag or similar tools",
            "Test deployment in development environment",
            "Verify resource configurations match requirements",
            "Check IAM permissions and security group rules",
            "Validate compliance with organizational policies"
        ]
    
    def _get_security_recommendations(self, issues: List[Dict[str, Any]]) -> List[str]:
        """Get security recommendations based on identified issues."""
        recommendations = []
        
        issue_types = [issue['type'] for issue in issues]
        
        if 'hardcoded_secrets' in issue_types:
            recommendations.append("Use AWS Secrets Manager or Systems Manager Parameter Store for sensitive data")
        
        if 'overly_permissive' in issue_types:
            recommendations.append("Apply principle of least privilege to IAM policies and security groups")
        
        if 'unencrypted_storage' in issue_types:
            recommendations.append("Enable encryption at rest for all storage services")
        
        return recommendations
