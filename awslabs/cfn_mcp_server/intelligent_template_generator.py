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

"""Intelligent CloudFormation template generation from natural language."""

import json
import yaml
import re
from typing import Dict, List, Any, Optional, Tuple
from awslabs.cfn_mcp_server.aws_client import get_aws_client

# Import config_manager only when needed to avoid circular dependencies
import importlib

# Get config_manager lazily
def get_config():
    from awslabs.cfn_mcp_server.config import config_manager
    return config_manager
from awslabs.cfn_mcp_server.architecture_templates import (
    generate_web_application_architecture,
    generate_serverless_api_architecture,
    generate_data_pipeline_architecture
)


class IntelligentTemplateGenerator:
    """Generates comprehensive CloudFormation templates from natural language descriptions."""
    
    def __init__(self, region: str = None, config=None):
        """Initialize the intelligent template generator.
        
        Args:
            region: AWS region for the template (defaults to configured default)
            config: Optional configuration manager instance
        """
        self.config = config or get_config()
        self.region = region or self.config.get_config('aws.default_region')
        self.client = get_aws_client('cloudformation', self.region)
        
        # Comprehensive resource patterns with context awareness
        self.resource_patterns = {
            # Compute Services
            'compute': {
                'patterns': [
                    r'\b(?:ec2|instance|server|vm|virtual machine|compute)\b',
                    r'\b(?:lambda|function|serverless|faas)\b',
                    r'\b(?:ecs|fargate|container|docker)\b',
                    r'\b(?:eks|kubernetes|k8s)\b',
                    r'\b(?:batch|job|processing)\b'
                ],
                'resources': {
                    'ec2': 'AWS::EC2::Instance',
                    'lambda': 'AWS::Lambda::Function',
                    'ecs': 'AWS::ECS::Service',
                    'eks': 'AWS::EKS::Cluster',
                    'batch': 'AWS::Batch::JobDefinition'
                }
            },
            
            # Storage Services
            'storage': {
                'patterns': [
                    r'\b(?:s3|bucket|storage|object store)\b',
                    r'\b(?:ebs|volume|disk)\b',
                    r'\b(?:efs|file system|nfs)\b',
                    r'\b(?:fsx|lustre|windows file)\b'
                ],
                'resources': {
                    's3': 'AWS::S3::Bucket',
                    'ebs': 'AWS::EC2::Volume',
                    'efs': 'AWS::EFS::FileSystem',
                    'fsx': 'AWS::FSx::FileSystem'
                }
            },
            
            # Database Services
            'database': {
                'patterns': [
                    r'\b(?:rds|database|db|mysql|postgres|oracle|sql server)\b',
                    r'\b(?:dynamodb|nosql|document|key-value)\b',
                    r'\b(?:aurora|cluster)\b',
                    r'\b(?:redshift|warehouse|analytics)\b',
                    r'\b(?:elasticache|redis|memcached|cache)\b'
                ],
                'resources': {
                    'rds': 'AWS::RDS::DBInstance',
                    'dynamodb': 'AWS::DynamoDB::Table',
                    'aurora': 'AWS::RDS::DBCluster',
                    'redshift': 'AWS::Redshift::Cluster',
                    'elasticache': 'AWS::ElastiCache::CacheCluster'
                }
            },
            
            # Networking Services
            'networking': {
                'patterns': [
                    r'\b(?:vpc|network|subnet)\b',
                    r'\b(?:alb|elb|load balancer|lb)\b',
                    r'\b(?:api gateway|api|rest|graphql)\b',
                    r'\b(?:cloudfront|cdn|distribution)\b',
                    r'\b(?:route53|dns|domain)\b',
                    r'\b(?:nat|gateway|internet gateway)\b'
                ],
                'resources': {
                    'vpc': 'AWS::EC2::VPC',
                    'alb': 'AWS::ElasticLoadBalancingV2::LoadBalancer',
                    'api': 'AWS::ApiGateway::RestApi',
                    'cloudfront': 'AWS::CloudFront::Distribution',
                    'route53': 'AWS::Route53::HostedZone',
                    'nat': 'AWS::EC2::NatGateway'
                }
            },
            
            # Security & Identity
            'security': {
                'patterns': [
                    r'\b(?:iam|role|policy|permission)\b',
                    r'\b(?:security group|firewall|sg)\b',
                    r'\b(?:kms|encryption|key|crypto)\b',
                    r'\b(?:secrets manager|secret|credential)\b',
                    r'\b(?:certificate|ssl|tls|acm)\b'
                ],
                'resources': {
                    'iam': 'AWS::IAM::Role',
                    'security_group': 'AWS::EC2::SecurityGroup',
                    'kms': 'AWS::KMS::Key',
                    'secrets': 'AWS::SecretsManager::Secret',
                    'certificate': 'AWS::CertificateManager::Certificate'
                }
            },
            
            # Monitoring & Logging
            'monitoring': {
                'patterns': [
                    r'\b(?:cloudwatch|alarm|metric|monitoring)\b',
                    r'\b(?:sns|notification|topic)\b',
                    r'\b(?:sqs|queue|message)\b',
                    r'\b(?:logs|logging|log group)\b'
                ],
                'resources': {
                    'cloudwatch': 'AWS::CloudWatch::Alarm',
                    'sns': 'AWS::SNS::Topic',
                    'sqs': 'AWS::SQS::Queue',
                    'logs': 'AWS::Logs::LogGroup'
                }
            },
            
            # Application Integration
            'integration': {
                'patterns': [
                    r'\b(?:step functions|workflow|state machine)\b',
                    r'\b(?:eventbridge|event|rule)\b',
                    r'\b(?:kinesis|stream|data stream)\b',
                    r'\b(?:firehose|delivery stream)\b'
                ],
                'resources': {
                    'stepfunctions': 'AWS::StepFunctions::StateMachine',
                    'eventbridge': 'AWS::Events::Rule',
                    'kinesis': 'AWS::Kinesis::Stream',
                    'firehose': 'AWS::KinesisFirehose::DeliveryStream'
                }
            }
        }
        
        # Architecture patterns for intelligent resource relationships
        self.architecture_patterns = {
            'web_application': {
                'keywords': ['web app', 'website', 'web application', 'frontend', 'backend'],
                'components': ['alb', 'ec2', 'rds', 'security_group', 'vpc']
            },
            'serverless_api': {
                'keywords': ['serverless', 'api', 'lambda api', 'rest api'],
                'components': ['lambda', 'api', 'dynamodb', 'iam']
            },
            'data_pipeline': {
                'keywords': ['data pipeline', 'etl', 'data processing', 'analytics'],
                'components': ['s3', 'lambda', 'kinesis', 'redshift', 'iam']
            },
            'microservices': {
                'keywords': ['microservices', 'containers', 'docker', 'ecs'],
                'components': ['ecs', 'alb', 'rds', 'vpc', 'security_group', 'iam']
            },
            'static_website': {
                'keywords': ['static site', 'static website', 'spa', 'single page'],
                'components': ['s3', 'cloudfront', 'route53', 'certificate']
            }
        }
    
    def analyze_description(self, description: str) -> Dict[str, Any]:
        """Analyze description to identify required AWS resources and architecture patterns."""
        description_lower = description.lower()
        
        # Identify architecture pattern
        architecture = self._identify_architecture_pattern(description_lower)
        
        # Identify individual resources
        identified_resources = self._identify_resources(description_lower)
        
        # Enhance with architecture-specific resources
        if architecture:
            arch_resources = self._get_architecture_resources(architecture)
            identified_resources.update(arch_resources)
        
        # Analyze scale and performance requirements
        scale_requirements = self._analyze_scale_requirements(description_lower)
        
        # Identify security requirements
        security_requirements = self._analyze_security_requirements(description_lower)
        
        return {
            'architecture_pattern': architecture,
            'resources': identified_resources,
            'scale_requirements': scale_requirements,
            'security_requirements': security_requirements,
            'original_description': description
        }
    
    def _identify_architecture_pattern(self, description: str) -> Optional[str]:
        """Identify the overall architecture pattern from description."""
        for pattern_name, pattern_info in self.architecture_patterns.items():
            for keyword in pattern_info['keywords']:
                if keyword in description:
                    return pattern_name
        return None
    
    def _identify_resources(self, description: str) -> Dict[str, str]:
        """Identify individual AWS resources from description."""
        identified = {}
        
        for category, category_info in self.resource_patterns.items():
            for pattern in category_info['patterns']:
                if re.search(pattern, description):
                    # Find the most specific resource type
                    for resource_key, resource_type in category_info['resources'].items():
                        if re.search(rf'\b{resource_key}\b', description):
                            identified[resource_key] = resource_type
                            break
                    else:
                        # Use the first resource type as default for the category
                        first_resource = list(category_info['resources'].items())[0]
                        identified[first_resource[0]] = first_resource[1]
        
        return identified
    
    def _get_architecture_resources(self, architecture: str) -> Dict[str, str]:
        """Get resources required for a specific architecture pattern."""
        if architecture not in self.architecture_patterns:
            return {}
        
        components = self.architecture_patterns[architecture]['components']
        resources = {}
        
        for component in components:
            # Find the resource type for this component
            for category_info in self.resource_patterns.values():
                if component in category_info['resources']:
                    resources[component] = category_info['resources'][component]
                    break
        
        return resources
    
    def _analyze_scale_requirements(self, description: str) -> Dict[str, Any]:
        """Analyze scale and performance requirements."""
        requirements = {
            'high_availability': False,
            'auto_scaling': False,
            'multi_az': False,
            'performance_tier': 'standard'
        }
        
        # High availability indicators
        ha_keywords = ['high availability', 'ha', 'fault tolerant', 'resilient', 'redundant']
        if any(keyword in description for keyword in ha_keywords):
            requirements['high_availability'] = True
            requirements['multi_az'] = True
        
        # Auto scaling indicators
        scaling_keywords = ['auto scaling', 'scale', 'elastic', 'variable load']
        if any(keyword in description for keyword in scaling_keywords):
            requirements['auto_scaling'] = True
        
        # Performance indicators
        if any(keyword in description for keyword in ['high performance', 'fast', 'low latency']):
            requirements['performance_tier'] = 'high'
        elif any(keyword in description for keyword in ['basic', 'simple', 'minimal']):
            requirements['performance_tier'] = 'basic'
        
        return requirements
    
    def _analyze_security_requirements(self, description: str) -> Dict[str, Any]:
        """Analyze security requirements."""
        requirements = {
            'encryption': False,
            'vpc_isolation': False,
            'iam_roles': True,  # Always recommended
            'security_groups': True,  # Always recommended
            'ssl_tls': False
        }
        
        # Encryption indicators
        if any(keyword in description for keyword in ['secure', 'encrypt', 'private', 'confidential']):
            requirements['encryption'] = True
        
        # VPC isolation indicators
        if any(keyword in description for keyword in ['private', 'isolated', 'vpc', 'internal']):
            requirements['vpc_isolation'] = True
        
        # SSL/TLS indicators
        if any(keyword in description for keyword in ['https', 'ssl', 'tls', 'certificate']):
            requirements['ssl_tls'] = True
        
        return requirements
    def generate_architecture_template(self, analysis: Dict[str, Any]) -> Dict[str, Dict[str, Any]]:
        """Generate a comprehensive template based on the identified architecture pattern.
        
        Args:
            analysis: Analysis dictionary containing requirements
            
        Returns:
            Dictionary of CloudFormation resources
        """
        architecture = analysis.get('architecture_pattern')
        
        if architecture == 'web_application':
            return generate_web_application_architecture(analysis, self.config)
        elif architecture == 'serverless_api':
            return generate_serverless_api_architecture(analysis, self.config)
        elif architecture == 'data_pipeline':
            return generate_data_pipeline_architecture(analysis, self.config)
        else:
            # If no specific architecture is identified, use the resource generator
            from awslabs.cfn_mcp_server.resource_generator import ResourceGenerator
            resource_gen = ResourceGenerator(self.config)
            return resource_gen.generate_resources(analysis)
    def create_discovery_prompt(self, description: str) -> Dict[str, Any]:
        """
        Create a discovery prompt for template generation.
        
        Args:
            description: Natural language description of the infrastructure
            
        Returns:
            Dict containing discovery prompt and analysis
        """
        try:
            # Analyze the description
            analysis = self.analyze_description(description)
            
            # Generate discovery questions
            discovery_questions = self._generate_discovery_questions(analysis)
            
            # Identify architecture patterns
            architecture_patterns = self._suggest_architecture_patterns(analysis)
            
            # Create requirements analysis
            requirements_analysis = self._analyze_requirements(description, analysis)
            
            # Generate expert prompt for Claude
            expert_prompt = self._create_expert_discovery_prompt(
                description, analysis, discovery_questions, architecture_patterns
            )
            
            return {
                'expert_prompt_for_claude': expert_prompt,
                'discovery_questions': discovery_questions,
                'architecture_patterns': architecture_patterns,
                'requirements_analysis': requirements_analysis,
                'initial_analysis': analysis
            }
            
        except Exception as e:
            return {
                'expert_prompt_for_claude': f"Error creating discovery prompt: {str(e)}",
                'error': str(e),
                'discovery_questions': [],
                'architecture_patterns': [],
                'requirements_analysis': {}
            }

    def _generate_discovery_questions(self, analysis: Dict[str, Any]) -> List[str]:
        """Generate discovery questions based on initial analysis."""
        questions = []
        
        # Base questions
        questions.extend([
            "What is the expected scale and traffic volume for this application?",
            "What are your availability and disaster recovery requirements?",
            "Are there specific compliance requirements (HIPAA, PCI, SOX, GDPR)?",
            "What is your preferred deployment model (single region, multi-region)?",
            "What are your security requirements and constraints?"
        ])
        
        # Resource-specific questions
        resources = analysis.get('resources', [])
        
        if 'database' in str(resources).lower():
            questions.extend([
                "What type of database workload (OLTP, OLAP, mixed)?",
                "What are your backup and retention requirements?",
                "Do you need read replicas or multi-master setup?"
            ])
        
        if 'web' in str(resources).lower() or 'api' in str(resources).lower():
            questions.extend([
                "What is the expected request rate and response time requirements?",
                "Do you need CDN or edge caching?",
                "What authentication and authorization mechanisms are required?"
            ])
        
        if 'storage' in str(resources).lower():
            questions.extend([
                "What are your data retention and lifecycle requirements?",
                "Do you need cross-region replication?",
                "What are your data access patterns (frequent, infrequent, archive)?"
            ])
        
        return questions[:10]  # Limit to 10 questions

    def _suggest_architecture_patterns(self, analysis: Dict[str, Any]) -> List[Dict[str, str]]:
        """Suggest architecture patterns based on analysis."""
        patterns = []
        
        architecture_pattern = analysis.get('architecture_pattern', '')
        resources = analysis.get('resources', [])
        
        if architecture_pattern == 'web-application':
            patterns.append({
                'name': '3-Tier Web Application',
                'description': 'Classic web application with presentation, application, and data tiers',
                'components': 'ALB + ECS/EC2 + RDS'
            })
            patterns.append({
                'name': 'Serverless Web Application',
                'description': 'Serverless architecture with API Gateway and Lambda',
                'components': 'CloudFront + API Gateway + Lambda + DynamoDB'
            })
        
        elif architecture_pattern == 'microservices':
            patterns.append({
                'name': 'Container-based Microservices',
                'description': 'Microservices using containers with service mesh',
                'components': 'EKS/ECS + Service Mesh + API Gateway'
            })
            patterns.append({
                'name': 'Serverless Microservices',
                'description': 'Event-driven serverless microservices',
                'components': 'API Gateway + Lambda + EventBridge + DynamoDB'
            })
        
        elif architecture_pattern == 'data-processing':
            patterns.append({
                'name': 'Batch Processing Pipeline',
                'description': 'Scheduled batch processing with data lake',
                'components': 'S3 + Glue + EMR + Redshift'
            })
            patterns.append({
                'name': 'Real-time Streaming',
                'description': 'Real-time data processing and analytics',
                'components': 'Kinesis + Lambda + ElasticSearch + S3'
            })
        
        # Default patterns if none match
        if not patterns:
            patterns.append({
                'name': 'Simple Web Application',
                'description': 'Basic web application with load balancer and database',
                'components': 'ALB + EC2 + RDS'
            })
        
        return patterns

    def _analyze_requirements(self, description: str, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze requirements from description and initial analysis."""
        return {
            'functional_requirements': self._extract_functional_requirements(description),
            'non_functional_requirements': self._extract_non_functional_requirements(description),
            'constraints': self._identify_constraints(description),
            'assumptions': self._identify_assumptions(analysis)
        }

    def _extract_functional_requirements(self, description: str) -> List[str]:
        """Extract functional requirements from description."""
        requirements = []
        desc_lower = description.lower()
        
        if 'web' in desc_lower or 'website' in desc_lower:
            requirements.append("Serve web content to users")
        
        if 'api' in desc_lower:
            requirements.append("Provide API endpoints for data access")
        
        if 'database' in desc_lower or 'data' in desc_lower:
            requirements.append("Store and retrieve application data")
        
        if 'auth' in desc_lower or 'login' in desc_lower:
            requirements.append("Authenticate and authorize users")
        
        if 'upload' in desc_lower or 'file' in desc_lower:
            requirements.append("Handle file uploads and storage")
        
        return requirements

    def _extract_non_functional_requirements(self, description: str) -> List[str]:
        """Extract non-functional requirements from description."""
        requirements = []
        desc_lower = description.lower()
        
        if 'scale' in desc_lower or 'high traffic' in desc_lower:
            requirements.append("Handle high traffic and scale automatically")
        
        if 'secure' in desc_lower or 'security' in desc_lower:
            requirements.append("Implement security best practices")
        
        if 'fast' in desc_lower or 'performance' in desc_lower:
            requirements.append("Provide fast response times")
        
        if 'available' in desc_lower or 'uptime' in desc_lower:
            requirements.append("Maintain high availability")
        
        return requirements

    def _identify_constraints(self, description: str) -> List[str]:
        """Identify constraints from description."""
        constraints = []
        desc_lower = description.lower()
        
        if 'budget' in desc_lower or 'cost' in desc_lower:
            constraints.append("Cost optimization required")
        
        if 'region' in desc_lower:
            constraints.append("Specific region requirements")
        
        if 'compliance' in desc_lower:
            constraints.append("Compliance requirements must be met")
        
        return constraints

    def _identify_assumptions(self, analysis: Dict[str, Any]) -> List[str]:
        """Identify assumptions based on analysis."""
        assumptions = [
            "AWS services are available in the target region",
            "Appropriate IAM permissions will be configured",
            "Network connectivity requirements will be met"
        ]
        
        if analysis.get('architecture_pattern') == 'web-application':
            assumptions.append("Internet-facing application with public access")
        
        return assumptions

    def _create_expert_discovery_prompt(self, description: str, analysis: Dict[str, Any], 
                                      questions: List[str], patterns: List[Dict[str, str]]) -> str:
        """Create expert discovery prompt for Claude."""
        return f"""
# CloudFormation Template Generation - Discovery Phase

## Initial Request
**Description**: {description}

## Initial Analysis
- **Architecture Pattern**: {analysis.get('architecture_pattern', 'Not determined')}
- **Identified Resources**: {', '.join(analysis.get('resources', []))}
- **Scale Requirements**: {analysis.get('scale_requirements', 'Not specified')}
- **Security Requirements**: {analysis.get('security_requirements', 'Standard')}

## Discovery Questions

To create the most appropriate CloudFormation template, I need to understand your requirements better. Please answer the following questions:

{chr(10).join([f"{i+1}. {q}" for i, q in enumerate(questions)])}

## Suggested Architecture Patterns

Based on your description, here are some architecture patterns to consider:

{chr(10).join([f"### {p['name']}{chr(10)}{p['description']}{chr(10)}**Components**: {p['components']}{chr(10)}" for p in patterns])}

## Next Steps

Once you provide answers to the discovery questions and select an architecture pattern, I will:

1. **Refine Requirements**: Create detailed technical specifications
2. **Design Architecture**: Develop comprehensive architecture diagrams
3. **Generate Template**: Create production-ready CloudFormation templates
4. **Provide Guidance**: Include deployment and operational guidance

Please answer the questions above, and let me know which architecture pattern best fits your needs, or if you'd like to explore other options.
"""
