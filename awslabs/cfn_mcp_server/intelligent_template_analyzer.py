"""
Intelligent CloudFormation Template Analysis Engine

This module provides advanced pattern recognition and expert prompt generation
for CloudFormation templates without complex parsing logic.
"""

import re
from typing import Dict, List, Any, Optional
from datetime import datetime


class IntelligentTemplateAnalyzer:
    """
    Intelligent template analyzer that focuses on pattern recognition
    and expert prompt generation rather than complex parsing.
    """
    
    def __init__(self):
        self.architecture_patterns = {
            'serverless': {
                'keywords': ['lambda', 'api gateway', 'dynamodb', 'step functions', 'sns', 'sqs'],
                'description': 'Serverless application architecture'
            },
            'web_application': {
                'keywords': ['alb', 'application load balancer', 'ec2', 'rds', 'cloudfront', 'route53'],
                'description': 'Traditional web application architecture'
            },
            'microservices': {
                'keywords': ['ecs', 'eks', 'fargate', 'service', 'container', 'api gateway'],
                'description': 'Containerized microservices architecture'
            },
            'data_pipeline': {
                'keywords': ['kinesis', 'glue', 'emr', 'redshift', 'athena', 'data', 'etl'],
                'description': 'Data processing and analytics pipeline'
            },
            'machine_learning': {
                'keywords': ['sagemaker', 'ml', 'model', 'training', 'inference', 'batch'],
                'description': 'Machine learning and AI workload'
            },
            'simple_storage': {
                'keywords': ['s3', 'bucket'],
                'description': 'Simple storage solution'
            },
            'networking': {
                'keywords': ['vpc', 'subnet', 'security group', 'nacl', 'route table'],
                'description': 'Network infrastructure setup'
            }
        }
        
        self.security_focus_areas = {
            'encryption': ['encryption', 'kms', 'ssl', 'tls'],
            'access_control': ['iam', 'policy', 'role', 'permission'],
            'network_security': ['security group', 'nacl', 'vpc', 'private'],
            'data_protection': ['backup', 'versioning', 'retention'],
            'monitoring': ['cloudtrail', 'cloudwatch', 'logging']
        }
        
        self.compliance_frameworks = {
            'HIPAA': ['encryption', 'audit', 'access control', 'data protection'],
            'PCI': ['encryption', 'network security', 'access control', 'monitoring'],
            'SOX': ['audit trail', 'access control', 'data integrity'],
            'GDPR': ['data protection', 'encryption', 'access control', 'retention']
        }

    def generate_intelligent_analysis_prompt(
        self, 
        template_content: str, 
        analysis_focus: Optional[str] = None,
        region: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Generate comprehensive expert analysis prompt with advanced pattern recognition.
        """
        # Perform advanced pattern recognition
        insights = self._analyze_template_patterns(template_content)
        
        # Generate context-aware expert prompt
        expert_prompt = self._create_expert_analysis_prompt(
            template_content, insights, analysis_focus, region
        )
        
        # Create interactive elements
        interactive_elements = self._create_interactive_elements(insights, analysis_focus)
        
        return {
            'success': True,
            'analysis_mode': 'intelligent_prompt',
            'template_insights': insights,
            'expert_prompt_for_claude': expert_prompt,
            'interactive_elements': interactive_elements,
            'analysis_workflow': self._create_analysis_workflow(analysis_focus),
            'best_practices_checklist': self._create_best_practices_checklist(insights, analysis_focus),
            'common_patterns': self._identify_common_patterns(insights),
            'region': region or 'us-east-1',
            'timestamp': datetime.utcnow().isoformat()
        }

    def _analyze_template_patterns(self, template_content: str) -> Dict[str, Any]:
        """Advanced pattern recognition on raw template content."""
        content_lower = template_content.lower()
        
        # Resource detection
        resources = self._detect_resources(template_content)
        
        # Architecture pattern detection
        architecture_pattern = self._detect_architecture_pattern(content_lower)
        
        # Complexity scoring
        complexity_score = self._calculate_complexity_score(template_content)
        
        # Risk area identification
        risk_areas = self._identify_risk_areas(content_lower)
        
        # Security concerns detection
        security_concerns = self._detect_security_concerns(content_lower)
        
        return {
            'resource_count': len(resources),
            'detected_resources': resources,
            'architecture_pattern': architecture_pattern,
            'complexity_score': complexity_score,
            'risk_areas': risk_areas,
            'security_concerns': security_concerns,
            'template_size': len(template_content),
            'has_parameters': 'parameters:' in content_lower,
            'has_outputs': 'outputs:' in content_lower,
            'has_conditions': 'conditions:' in content_lower
        }

    def _detect_resources(self, template_content: str) -> List[str]:
        """Detect AWS resource types in template."""
        # Pattern to match AWS resource types
        resource_pattern = r'Type:\s*["\']?(AWS::[A-Za-z0-9]+::[A-Za-z0-9]+)["\']?'
        matches = re.findall(resource_pattern, template_content, re.IGNORECASE)
        return list(set(matches))

    def _detect_architecture_pattern(self, content_lower: str) -> str:
        """Detect primary architecture pattern."""
        pattern_scores = {}
        
        for pattern, config in self.architecture_patterns.items():
            score = sum(1 for keyword in config['keywords'] if keyword in content_lower)
            if score > 0:
                pattern_scores[pattern] = score
        
        if pattern_scores:
            return max(pattern_scores, key=pattern_scores.get)
        return 'custom'

    def _calculate_complexity_score(self, template_content: str) -> int:
        """Calculate template complexity (1-10)."""
        lines = len(template_content.split('\n'))
        resource_count = len(re.findall(r'Type:\s*AWS::', template_content, re.IGNORECASE))
        
        # Simple scoring algorithm
        score = min(10, (lines // 50) + (resource_count * 2))
        return max(1, score)

    def _identify_risk_areas(self, content_lower: str) -> List[str]:
        """Identify potential risk areas."""
        risk_areas = []
        
        for area, keywords in self.security_focus_areas.items():
            if any(keyword in content_lower for keyword in keywords):
                risk_areas.append(area)
        
        # Check for missing security configurations
        if 's3' in content_lower and 'encryption' not in content_lower:
            risk_areas.append('missing_encryption')
        
        if 'rds' in content_lower and 'encrypted' not in content_lower:
            risk_areas.append('missing_database_encryption')
            
        return risk_areas

    def _detect_security_concerns(self, content_lower: str) -> List[str]:
        """Detect specific security concerns."""
        concerns = []
        
        # Check for hardcoded values
        if re.search(r'password.*[:=]\s*["\'][^"\']+["\']', content_lower):
            concerns.append('potential_hardcoded_secrets')
        
        # Check for overly permissive policies
        if '*' in content_lower and ('action' in content_lower or 'resource' in content_lower):
            concerns.append('overly_permissive_policies')
        
        # Check for public access
        if 'public' in content_lower:
            concerns.append('public_access_configuration')
            
        return concerns

    def _create_expert_analysis_prompt(
        self, 
        template_content: str, 
        insights: Dict[str, Any], 
        analysis_focus: Optional[str],
        region: Optional[str]
    ) -> str:
        """Create comprehensive expert analysis prompt."""
        
        focus_guidance = {
            'security': 'Focus on security vulnerabilities, encryption, access controls, and compliance.',
            'performance': 'Focus on performance optimization, resource sizing, and efficiency.',
            'compliance': 'Focus on regulatory compliance, audit requirements, and governance.',
            'architecture': 'Focus on architectural patterns, best practices, and design principles.',
            'cost': 'Focus on cost optimization, resource efficiency, and billing impact.'
        }
        
        architecture_desc = self.architecture_patterns.get(
            insights['architecture_pattern'], 
            {'description': 'Custom architecture'}
        )['description']
        
        prompt = f"""
# Expert CloudFormation Template Analysis

You are a senior AWS CloudFormation architect with deep expertise in cloud infrastructure, security, and best practices.

## TEMPLATE ANALYSIS CONTEXT

**Architecture Pattern**: {architecture_desc}
**Complexity Score**: {insights['complexity_score']}/10
**Resource Count**: {insights['resource_count']}
**Template Size**: {insights['template_size']} characters
**Region Context**: {region or 'us-east-1'}
**Analysis Focus**: {analysis_focus or 'comprehensive'}

{focus_guidance.get(analysis_focus, 'Provide comprehensive analysis covering security, performance, compliance, and architectural best practices.')}

**Detected Resources**: {', '.join(insights['detected_resources'][:10])}{'...' if len(insights['detected_resources']) > 10 else ''}

**Risk Areas Identified**: {', '.join(insights['risk_areas']) if insights['risk_areas'] else 'None detected'}

## GUIDED ANALYSIS FRAMEWORK

### Phase 1: Template Structure Assessment
□ Validate CloudFormation syntax and structure
□ Review resource definitions and properties
□ Check parameter usage and validation
□ Assess output definitions and exports

### Phase 2: Security Deep Dive
□ Encryption configurations (at-rest and in-transit)
□ IAM roles, policies, and permissions
□ Network security (VPC, Security Groups, NACLs)
□ Data protection and backup strategies
□ Secrets management and credential handling

### Phase 3: Architecture Review
□ Resource relationships and dependencies
□ Scalability and availability design
□ Fault tolerance and disaster recovery
□ Service integration patterns
□ Cost optimization opportunities

### Phase 4: Interactive Analysis Questions

Based on your findings above, please answer these critical questions:

1. **Security Assessment**: What are the top 3 security risks in this template?
2. **Compliance Impact**: Which compliance frameworks might be affected by current configurations?
3. **Performance Concerns**: Are there any resource configurations that could impact performance?
4. **Cost Implications**: What are the potential cost drivers and optimization opportunities?
5. **Operational Readiness**: Is this template ready for production deployment?

### Phase 5: Specific Recommendations

For each issue identified, provide:
- **Issue Description**: Clear explanation of the problem
- **Risk Level**: HIGH/MEDIUM/LOW with justification
- **CloudFormation Fix**: Specific property additions/changes
- **Code Example**: Working CloudFormation snippet
- **Best Practice Rationale**: Why this fix follows AWS best practices

## TEMPLATE CONTENT FOR ANALYSIS

```yaml
{template_content}
```

## ANALYSIS DELIVERABLES

Please provide:
1. **Executive Summary**: High-level findings and recommendations
2. **Detailed Security Analysis**: Comprehensive security assessment
3. **Architecture Evaluation**: Design patterns and improvements
4. **Compliance Review**: Regulatory and governance considerations
5. **Implementation Roadmap**: Prioritized list of fixes and improvements
6. **Production Readiness Checklist**: Go/no-go criteria for deployment

Focus on actionable, specific recommendations with working CloudFormation code examples.
"""
        
        return prompt

    def _create_interactive_elements(self, insights: Dict[str, Any], analysis_focus: Optional[str]) -> Dict[str, Any]:
        """Create interactive elements for guided analysis."""
        return {
            'guided_questions': self._create_guided_questions(insights, analysis_focus),
            'checklist_items': self._create_checklist_items(insights),
            'exploration_areas': self._create_exploration_areas(insights)
        }

    def _create_guided_questions(self, insights: Dict[str, Any], analysis_focus: Optional[str]) -> List[str]:
        """Create context-aware guided questions."""
        questions = [
            "What is the primary purpose of this CloudFormation template?",
            "Are all resources properly configured for the intended use case?",
            "What security measures are currently implemented?"
        ]
        
        if 's3' in str(insights['detected_resources']).lower():
            questions.extend([
                "Are S3 buckets configured with appropriate encryption?",
                "Do S3 buckets have public access restrictions enabled?",
                "Is versioning enabled for data protection?"
            ])
        
        if 'rds' in str(insights['detected_resources']).lower():
            questions.extend([
                "Are RDS instances configured with encryption at rest?",
                "Is Multi-AZ enabled for high availability?",
                "Are automated backups properly configured?"
            ])
        
        if analysis_focus == 'security':
            questions.extend([
                "Are there any hardcoded secrets or credentials?",
                "Do IAM policies follow the principle of least privilege?",
                "Are all network communications properly secured?"
            ])
        
        return questions

    def _create_analysis_workflow(self, analysis_focus: Optional[str]) -> List[str]:
        """Create analysis workflow steps."""
        base_workflow = [
            "Template Structure Validation",
            "Resource Configuration Review",
            "Security Assessment",
            "Best Practices Evaluation"
        ]
        
        focus_workflows = {
            'security': base_workflow + ["Threat Modeling", "Compliance Check"],
            'performance': base_workflow + ["Performance Analysis", "Optimization Review"],
            'compliance': base_workflow + ["Regulatory Assessment", "Audit Preparation"],
            'cost': base_workflow + ["Cost Analysis", "Optimization Opportunities"]
        }
        
        return focus_workflows.get(analysis_focus, base_workflow + ["Comprehensive Review"])

    def _create_best_practices_checklist(self, insights: Dict[str, Any], analysis_focus: Optional[str]) -> List[str]:
        """Create context-aware best practices checklist."""
        checklist = [
            "✓ All resources have appropriate tags for governance",
            "✓ IAM roles follow least privilege principle",
            "✓ Encryption enabled for data at rest and in transit",
            "✓ Network security properly configured",
            "✓ Monitoring and logging enabled",
            "✓ Backup and disaster recovery planned"
        ]
        
        # Add resource-specific items
        if 's3' in str(insights['detected_resources']).lower():
            checklist.extend([
                "✓ S3 buckets have encryption enabled",
                "✓ S3 public access is properly restricted",
                "✓ S3 versioning enabled where appropriate"
            ])
        
        if 'lambda' in str(insights['detected_resources']).lower():
            checklist.extend([
                "✓ Lambda functions have appropriate memory allocation",
                "✓ Lambda timeout values are optimized",
                "✓ Lambda environment variables secured"
            ])
        
        return checklist

    def _create_checklist_items(self, insights: Dict[str, Any]) -> List[str]:
        """Create interactive checklist items."""
        return [
            "Template syntax is valid",
            "All required parameters are defined",
            "Resource dependencies are properly configured",
            "Security best practices are followed",
            "Cost optimization opportunities identified"
        ]

    def _create_exploration_areas(self, insights: Dict[str, Any]) -> List[str]:
        """Create areas for deeper exploration."""
        areas = ["Security Configuration", "Performance Optimization", "Cost Management"]
        
        if insights['architecture_pattern'] == 'serverless':
            areas.append("Serverless Best Practices")
        elif insights['architecture_pattern'] == 'web_application':
            areas.append("Web Application Security")
        
        return areas

    def _identify_common_patterns(self, insights: Dict[str, Any]) -> List[Dict[str, str]]:
        """Identify common patterns and provide guidance."""
        patterns = []
        
        if insights['architecture_pattern'] == 'simple_storage':
            patterns.append({
                'pattern': 'S3 Storage Setup',
                'guidance': 'Ensure encryption, versioning, and public access controls are properly configured'
            })
        
        if 'missing_encryption' in insights['risk_areas']:
            patterns.append({
                'pattern': 'Missing Encryption',
                'guidance': 'Add encryption configuration to all storage and database resources'
            })
        
        return patterns
