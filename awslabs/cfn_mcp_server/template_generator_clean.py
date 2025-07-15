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

"""
Clean Template Generator - Pure Prompt Enhancement

This module transforms basic infrastructure requests into comprehensive expert prompts
that guide Claude through creating superior CloudFormation templates.

Key Focus:
- Detect architecture patterns and compliance requirements
- Create expert-level template generation prompts
- Provide comprehensive guidance and best practices
- Include follow-up questions and validation checklists
"""

import re
from typing import Dict, List, Any, Optional

class TemplateGenerator:
    """
    Enhances basic template requests into comprehensive expert prompts.
    
    This class analyzes user requests and creates detailed prompts that help Claude
    provide superior CloudFormation templates with proper architecture patterns,
    security best practices, and compliance requirements.
    """
    
    def __init__(self):
        """Initialize the template generator with pattern recognition."""
        self.architecture_patterns = {
            "web_application": {
                "keywords": ["web app", "website", "frontend", "backend", "api", "load balancer", "alb", "elb"],
                "components": ["Load Balancer", "Auto Scaling", "Database", "CDN", "Security Groups"],
                "services": ["ALB/ELB", "EC2/ECS/Lambda", "RDS/DynamoDB", "CloudFront", "VPC"]
            },
            "microservices": {
                "keywords": ["microservice", "container", "docker", "kubernetes", "ecs", "fargate", "service mesh"],
                "components": ["Container Orchestration", "Service Discovery", "API Gateway", "Message Queue"],
                "services": ["ECS/EKS", "Service Discovery", "API Gateway", "SQS/SNS"]
            },
            "data_processing": {
                "keywords": ["data", "analytics", "etl", "pipeline", "stream", "batch", "kinesis", "glue"],
                "components": ["Data Ingestion", "Processing Engine", "Data Storage", "Analytics"],
                "services": ["Kinesis/SQS", "Lambda/EMR/Glue", "S3/RDS/Redshift", "QuickSight"]
            },
            "serverless": {
                "keywords": ["serverless", "lambda", "api gateway", "dynamodb", "s3", "event-driven"],
                "components": ["Function Compute", "API Management", "Event Sources", "Data Storage"],
                "services": ["Lambda", "API Gateway", "DynamoDB/S3", "EventBridge/SQS"]
            },
            "machine_learning": {
                "keywords": ["ml", "machine learning", "ai", "sagemaker", "model", "training", "inference"],
                "components": ["Model Training", "Model Hosting", "Data Pipeline", "Monitoring"],
                "services": ["SageMaker", "S3", "Lambda", "CloudWatch"]
            }
        }
        
        self.compliance_patterns = {
            "hipaa": {
                "keywords": ["hipaa", "healthcare", "medical", "patient", "phi", "health"],
                "requirements": ["Encryption at rest and transit", "Audit logging", "Access controls", "Data backup"]
            },
            "pci_dss": {
                "keywords": ["pci", "payment", "credit card", "financial", "transaction"],
                "requirements": ["Network segmentation", "Encryption", "Access monitoring", "Vulnerability scanning"]
            },
            "gdpr": {
                "keywords": ["gdpr", "privacy", "personal data", "eu", "european"],
                "requirements": ["Data protection", "Right to erasure", "Consent management", "Data portability"]
            },
            "sox": {
                "keywords": ["sox", "sarbanes", "oxley", "financial reporting", "audit"],
                "requirements": ["Audit trails", "Change management", "Access controls", "Data integrity"]
            },
            "fedramp": {
                "keywords": ["fedramp", "federal", "government", "compliance"],
                "requirements": ["Security controls", "Continuous monitoring", "Incident response", "Risk assessment"]
            }
        }
        
        self.scale_indicators = {
            "small": ["small", "startup", "prototype", "development", "test"],
            "medium": ["medium", "production", "business", "enterprise"],
            "large": ["large", "scale", "high traffic", "millions", "global"]
        }
    
    def generate_enhanced_prompt(
        self,
        description: str,
        template_format: str = "YAML",
        region: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Generate an enhanced expert prompt for CloudFormation template creation.
        
        This method analyzes the user's description and creates a comprehensive
        prompt that guides Claude through creating superior templates.
        """
        
        # Analyze the user's request
        analysis = self._analyze_request(description)
        
        # Create the expert prompt
        expert_prompt = self._create_expert_template_prompt(
            original_request=description,
            analysis=analysis,
            template_format=template_format,
            region=region
        )
        
        # Generate follow-up questions
        follow_up_questions = self._generate_follow_up_questions(analysis)
        
        # Create best practices checklist
        best_practices = self._create_best_practices_checklist(analysis)
        
        # Create implementation guide
        implementation_guide = self._create_implementation_guide(analysis)
        
        # Create validation checklist
        validation_checklist = self._create_validation_checklist(analysis)
        
        return {
            "expert_prompt_for_claude": expert_prompt,
            "original_request": description,
            "enhanced_context": {
                "architecture_type": analysis["architecture_type"],
                "compliance_requirements": analysis["compliance_requirements"],
                "environment": analysis["environment"],
                "scale": analysis["scale"]
            },
            "follow_up_questions": follow_up_questions,
            "best_practices_checklist": best_practices,
            "implementation_guide": implementation_guide,
            "validation_checklist": validation_checklist,
            "suggested_workflow": [
                "1. Review and customize the generated template",
                "2. Validate template syntax and logic",
                "3. Deploy to development environment first",
                "4. Test all functionality and integrations",
                "5. Review security and compliance requirements",
                "6. Deploy to production with monitoring",
                "7. Set up ongoing maintenance procedures"
            ],
            "template_format": template_format,
            "region": region or "us-east-1"
        }
    
    def _analyze_request(self, description: str) -> Dict[str, Any]:
        """Analyze the user's request to identify patterns and requirements."""
        
        description_lower = description.lower()
        
        # Enhanced pattern detection with context awareness
        architecture_analysis = self._detect_architecture_with_context(description_lower)
        architecture_type = architecture_analysis["primary_type"]
        architecture_confidence = architecture_analysis["confidence"]
        conflicting_patterns = architecture_analysis["conflicts"]
        
        # Detect implicit requirements based on context
        implicit_requirements = self._detect_implicit_requirements(description_lower, architecture_type)
        
        # Detect compliance requirements
        compliance_requirements = []
        for compliance, patterns in self.compliance_patterns.items():
            if any(keyword in description_lower for keyword in patterns["keywords"]):
                compliance_requirements.append(compliance)
        
        # Detect scale
        scale = "medium"  # default
        for scale_type, indicators in self.scale_indicators.items():
            if any(indicator in description_lower for indicator in indicators):
                scale = scale_type
                break
        
        # Detect environment
        environment = "production"  # default
        if any(word in description_lower for word in ["dev", "development", "test", "staging"]):
            environment = "development"
        elif any(word in description_lower for word in ["prod", "production", "live"]):
            environment = "production"
        
        return {
            "architecture_type": architecture_type,
            "architecture_confidence": architecture_confidence,
            "compliance_requirements": compliance_requirements,
            "scale": scale,
            "environment": environment,
            "keywords": re.findall(r'\b\w+\b', description_lower)
        }
    
    def _create_expert_template_prompt(
        self,
        original_request: str,
        analysis: Dict[str, Any],
        template_format: str,
        region: Optional[str]
    ) -> str:
        """Create a comprehensive expert prompt for template generation."""
        
        architecture_type = analysis["architecture_type"]
        compliance_requirements = analysis["compliance_requirements"]
        scale = analysis["scale"]
        environment = analysis["environment"]
        
        prompt = f"""

You are an expert AWS Solutions Architect specializing in CloudFormation. Create a comprehensive, production-ready CloudFormation template based on this request:

ORIGINAL REQUEST: {original_request}

REQUIREMENTS ANALYSIS:
- Architecture Type: {architecture_type}
- Environment: {environment}
- Scale: {scale}
- Compliance: {compliance_requirements}

Please create a CloudFormation template that includes:

ARCHITECTURE REQUIREMENTS:
"""
        
        # Add architecture-specific requirements
        if architecture_type in self.architecture_patterns:
            pattern = self.architecture_patterns[architecture_type]
            prompt += f"- {', '.join(pattern['components'])}\n"
            prompt += f"- Recommended Services: {', '.join(pattern['services'])}\n"
        
        if architecture_type == "web_application":
            prompt += """- Load balancing and auto-scaling capabilities
- Database layer with backup and recovery
- CDN for static content delivery
- Proper network segmentation with VPC
- Security groups with least privilege access
"""
        elif architecture_type == "microservices":
            prompt += """- Container orchestration platform
- Service discovery and load balancing
- API gateway for external access
- Inter-service communication patterns
- Centralized logging and monitoring
"""
        elif architecture_type == "data_processing":
            prompt += """- Data ingestion layer (Kinesis/SQS)
- Processing compute (Lambda/EMR/Glue)
- Data storage (S3/RDS/DynamoDB)
- Data catalog and governance
- Monitoring and alerting
"""
        elif architecture_type == "serverless":
            prompt += """- Event-driven architecture with Lambda
- API Gateway for HTTP endpoints
- Managed databases (DynamoDB)
- Event sources and triggers
- Serverless monitoring and observability
"""
        elif architecture_type == "machine_learning":
            prompt += """- Model training infrastructure
- Model hosting and inference endpoints
- Data pipeline for ML workflows
- Experiment tracking and versioning
- Model monitoring and performance tracking
"""
        
        prompt += """
SECURITY REQUIREMENTS:
- Encryption at rest and in transit
- Least privilege IAM policies
- Security groups with minimal necessary access
- VPC with proper network segmentation
- CloudTrail logging enabled
- GuardDuty integration where applicable
"""
        
        # Add compliance-specific requirements
        for compliance in compliance_requirements:
            if compliance == "hipaa":
                prompt += """
HIPAA COMPLIANCE:
- All PHI data encrypted with AES-256
- Comprehensive audit logging enabled
- Access controls with role-based permissions
- Data backup with encryption
- Network segmentation and isolation
- Business Associate Agreements documented
"""
            elif compliance == "pci_dss":
                prompt += """
PCI DSS COMPLIANCE:
- Network segmentation for cardholder data
- Strong encryption for data transmission
- Regular security testing and monitoring
- Access control measures
- Vulnerability management program
"""
            elif compliance == "gdpr":
                prompt += """
GDPR COMPLIANCE:
- Data protection by design and default
- Consent management mechanisms
- Right to erasure capabilities
- Data portability features
- Privacy impact assessments
"""
        
        prompt += f"""
OPERATIONAL REQUIREMENTS:
- CloudWatch monitoring and alarms
- Centralized logging with CloudWatch Logs
- Automated backup strategies
- Disaster recovery considerations
- Cost optimization with appropriate resource sizing
- Resource tagging for governance
- Infrastructure as Code best practices

DELIVERABLES:
1. Complete CloudFormation template ({template_format} format)
2. Parameter definitions with descriptions
3. Output values for key resources
4. Deployment instructions
5. Security considerations summary
6. Cost estimation guidance
7. Monitoring and alerting recommendations

Please ensure the template follows AWS Well-Architected Framework principles and includes comprehensive documentation.


ADDITIONAL SPECIFICATIONS:
- Output Format: {template_format}
- Target Region: {region or 'us-east-1'}
- Follow AWS Well-Architected Framework principles
- Include comprehensive parameter descriptions
- Add meaningful output values
- Use latest resource properties and best practices

TEMPLATE STRUCTURE REQUIREMENTS:
1. AWSTemplateFormatVersion: '2010-09-09'
2. Description: Clear, comprehensive description
3. Parameters: Well-documented with constraints and defaults
4. Conditions: If needed for environment-specific logic
5. Resources: All necessary resources with proper dependencies
6. Outputs: Key resource identifiers and endpoints

DOCUMENTATION REQUIREMENTS:
Please also provide:
1. Architecture overview and component relationships
2. Deployment prerequisites and steps
3. Post-deployment configuration tasks
4. Security configuration summary
5. Cost optimization recommendations
6. Monitoring and maintenance guidance
7. Troubleshooting common issues

Make the template production-ready with enterprise-grade security, monitoring, and operational excellence.
"""
        
        return prompt
    
    def _generate_follow_up_questions(self, analysis: Dict[str, Any]) -> List[str]:
        """Generate relevant follow-up questions based on the analysis."""
        
        questions = [
            "What is your expected traffic volume or usage patterns?",
            "Do you have specific RTO/RPO requirements for disaster recovery?",
            "What is your monthly budget target for this infrastructure?",
            "Are there any existing systems this needs to integrate with?",
            "What are your data retention and backup requirements?"
        ]
        
        architecture_type = analysis["architecture_type"]
        
        if architecture_type == "web_application":
            questions.extend([
                "What is your expected number of concurrent users?",
                "Do you need multi-region deployment for high availability?",
                "What are your database performance requirements?"
            ])
        elif architecture_type == "data_processing":
            questions.extend([
                "What is your data volume and processing frequency?",
                "Do you need real-time or batch processing?",
                "What data formats will you be working with?"
            ])
        elif architecture_type == "microservices":
            questions.extend([
                "How many services do you plan to deploy initially?",
                "Do you need service mesh capabilities?",
                "What are your container orchestration preferences?"
            ])
        elif architecture_type == "serverless":
            questions.extend([
                "What are your expected function invocation rates?",
                "Do you need synchronous or asynchronous processing?",
                "What are your cold start latency requirements?"
            ])
        
        if analysis["compliance_requirements"]:
            questions.extend([
                "What specific compliance certifications do you need?",
                "Do you have existing compliance frameworks to follow?",
                "What are your audit and reporting requirements?"
            ])
        
        return questions
    
    def _create_best_practices_checklist(self, analysis: Dict[str, Any]) -> List[str]:
        """Create a best practices checklist based on the analysis."""
        
        checklist = [
            "✓ All resources have appropriate tags",
            "✓ IAM roles follow least privilege principle",
            "✓ Encryption enabled for data at rest and in transit",
            "✓ CloudWatch monitoring configured",
            "✓ Backup and recovery procedures defined",
            "✓ Security groups restrict access appropriately",
            "✓ Cost optimization measures implemented"
        ]
        
        # Add compliance-specific items
        for compliance in analysis["compliance_requirements"]:
            if compliance == "hipaa":
                checklist.extend([
                    "✓ PHI data encryption verified",
                    "✓ Audit logging comprehensive",
                    "✓ Access controls documented"
                ])
            elif compliance == "pci_dss":
                checklist.extend([
                    "✓ Network segmentation implemented",
                    "✓ Cardholder data encrypted",
                    "✓ Access monitoring enabled"
                ])
        
        # Add architecture-specific items
        architecture_type = analysis["architecture_type"]
        if architecture_type == "web_application":
            checklist.extend([
                "✓ Load balancer health checks configured",
                "✓ Auto-scaling policies defined",
                "✓ Database backup strategy implemented"
            ])
        elif architecture_type == "microservices":
            checklist.extend([
                "✓ Service discovery configured",
                "✓ Inter-service communication secured",
                "✓ Container health checks enabled"
            ])
        
        return checklist
    
    def _create_implementation_guide(self, analysis: Dict[str, Any]) -> Dict[str, List[str]]:
        """Create an implementation guide with specific steps."""
        
        return {
            "pre_deployment": [
                "Review and customize template parameters",
                "Ensure AWS CLI is configured with appropriate permissions",
                "Validate template syntax: aws cloudformation validate-template",
                "Check service limits and quotas in target region",
                "Prepare any external dependencies (certificates, DNS, etc.)"
            ],
            "deployment_steps": [
                "Deploy to development environment first",
                "Test all functionality and integrations",
                "Run security and compliance validation",
                "Deploy to staging for final testing",
                "Deploy to production with monitoring enabled"
            ],
            "post_deployment": [
                "Verify all resources are healthy",
                "Configure monitoring and alerting",
                "Test backup and recovery procedures",
                "Document operational procedures",
                "Set up ongoing maintenance schedules"
            ],
            "cli_commands": [
                "aws cloudformation create-stack --stack-name <n> --template-body file://template.yaml",
                "aws cloudformation describe-stacks --stack-name <n>",
                "aws cloudformation describe-stack-events --stack-name <n>",
                "aws cloudformation get-template --stack-name <n>"
            ]
        }
    
    def _create_validation_checklist(self, analysis: Dict[str, Any]) -> List[str]:
        """Create a validation checklist for the generated template."""
        
        checklist = [
            "✓ Template syntax is valid YAML/JSON",
            "✓ All required parameters have appropriate defaults or constraints",
            "✓ Resource dependencies are properly defined",
            "✓ IAM roles and policies follow least privilege",
            "✓ Security groups have minimal necessary access",
            "✓ Encryption is enabled for data at rest and in transit",
            "✓ Monitoring and logging are configured",
            "✓ Resource tags are comprehensive and consistent",
            "✓ Cost optimization measures are implemented",
            "✓ Backup and disaster recovery are addressed"
        ]
        
        # Add compliance-specific validation
        for compliance in analysis["compliance_requirements"]:
            if compliance == "hipaa":
                checklist.extend([
                    "✓ PHI data encryption verified (AES-256)",
                    "✓ Audit logging is comprehensive and tamper-proof",
                    "✓ Access controls are role-based and documented"
                ])
            elif compliance == "pci_dss":
                checklist.extend([
                    "✓ Network segmentation isolates cardholder data",
                    "✓ Encryption meets PCI DSS requirements",
                    "✓ Access monitoring and logging enabled"
                ])
        
        return checklist
    def _detect_architecture_with_context(self, description_lower: str) -> Dict[str, Any]:
        """Enhanced architecture detection with context awareness and conflict resolution."""
        
        pattern_scores = {}
        
        # Score each architecture pattern
        for arch_type, patterns in self.architecture_patterns.items():
            score = 0
            matched_keywords = []
            
            for keyword in patterns["keywords"]:
                if keyword in description_lower:
                    # Weight keywords based on specificity
                    weight = self._get_keyword_weight(keyword, arch_type)
                    score += weight
                    matched_keywords.append(keyword)
            
            if score > 0:
                pattern_scores[arch_type] = {
                    "score": score,
                    "matched_keywords": matched_keywords,
                    "confidence": min(score / len(patterns["keywords"]), 1.0)
                }
        
        # Resolve conflicts and determine primary architecture
        if not pattern_scores:
            return {"primary_type": "general", "confidence": 0, "conflicts": []}
        
        # Sort by score
        sorted_patterns = sorted(pattern_scores.items(), key=lambda x: x[1]["score"], reverse=True)
        primary_type = sorted_patterns[0][0]
        primary_confidence = sorted_patterns[0][1]["confidence"]
        
        # Detect conflicts (multiple high-scoring patterns)
        conflicts = []
        if len(sorted_patterns) > 1:
            second_score = sorted_patterns[1][1]["score"]
            if second_score > 0.3 * sorted_patterns[0][1]["score"]:  # Within 30% of top score
                conflicts = [pattern[0] for pattern in sorted_patterns[1:3]]
        
        return {
            "primary_type": primary_type,
            "confidence": primary_confidence,
            "conflicts": conflicts,
            "all_scores": pattern_scores
        }
    
    def _get_keyword_weight(self, keyword: str, arch_type: str) -> float:
        """Assign weights to keywords based on specificity and context."""
        
        # High-specificity keywords get higher weights
        high_specificity = {
            "kubernetes": 2.0, "k8s": 2.0, "fargate": 2.0, "sagemaker": 2.0,
            "kinesis": 1.8, "glue": 1.8, "emr": 1.8, "redshift": 1.8,
            "api gateway": 1.5, "lambda": 1.5, "dynamodb": 1.5
        }
        
        # Medium-specificity keywords
        medium_specificity = {
            "microservice": 1.2, "container": 1.2, "serverless": 1.2,
            "analytics": 1.2, "pipeline": 1.2, "stream": 1.2
        }
        
        # Low-specificity keywords (common terms)
        low_specificity = {
            "web": 0.8, "app": 0.8, "data": 0.8, "api": 0.8,
            "database": 0.8, "storage": 0.8
        }
        
        if keyword in high_specificity:
            return high_specificity[keyword]
        elif keyword in medium_specificity:
            return medium_specificity[keyword]
        elif keyword in low_specificity:
            return low_specificity[keyword]
        else:
            return 1.0  # Default weight
    
    def _detect_implicit_requirements(self, description_lower: str, architecture_type: str) -> Dict[str, List[str]]:
        """Detect implicit requirements based on context and architecture type."""
        
        implicit_reqs = {
            "security": [],
            "performance": [],
            "operational": [],
            "compliance": []
        }
        
        # Architecture-specific implicit requirements
        if architecture_type == "web_application":
            implicit_reqs["security"].extend([
                "WAF for application protection",
                "SSL/TLS certificates", 
                "Security headers configuration"
            ])
            implicit_reqs["performance"].extend([
                "CDN for static content",
                "Auto-scaling for traffic spikes",
                "Database connection pooling"
            ])
            implicit_reqs["operational"].extend([
                "Health checks and monitoring",
                "Log aggregation",
                "Backup strategies"
            ])
        
        elif architecture_type == "microservices":
            implicit_reqs["security"].extend([
                "Service-to-service authentication",
                "Network segmentation",
                "Secrets management"
            ])
            implicit_reqs["performance"].extend([
                "Service discovery",
                "Load balancing", 
                "Circuit breakers"
            ])
            implicit_reqs["operational"].extend([
                "Distributed tracing",
                "Centralized logging",
                "Container health checks"
            ])
        
        elif architecture_type == "data_processing":
            implicit_reqs["security"].extend([
                "Data encryption at rest",
                "Data access controls",
                "Audit logging"
            ])
            implicit_reqs["performance"].extend([
                "Data partitioning",
                "Parallel processing",
                "Caching strategies"
            ])
            implicit_reqs["operational"].extend([
                "Data quality monitoring",
                "Pipeline orchestration", 
                "Error handling and retries"
            ])
        
        # Context-based implicit requirements
        if any(word in description_lower for word in ["production", "prod", "live"]):
            implicit_reqs["operational"].extend([
                "Multi-AZ deployment",
                "Automated backups",
                "Disaster recovery plan"
            ])
        
        if any(word in description_lower for word in ["high traffic", "scale", "millions"]):
            implicit_reqs["performance"].extend([
                "Auto-scaling groups",
                "Read replicas",
                "Caching layers"
            ])
        
        if any(word in description_lower for word in ["secure", "security", "compliance"]):
            implicit_reqs["security"].extend([
                "Encryption in transit",
                "IAM least privilege",
                "Security monitoring"
            ])
        
        return implicit_reqs 
    
    def _create_refinement_prompt_from_discovery(self, original_description: str, analysis: dict, discovery_response: str) -> str:
        """Create a refinement prompt based on discovery responses."""
        
        return f"""
You are an expert AWS Solutions Architect refining architecture requirements.

ORIGINAL REQUEST: "{original_description}"

INITIAL ANALYSIS:
- Architecture Type: {analysis.get('architecture_type', 'Unknown')}
- Confidence: {analysis.get('architecture_confidence', 0)*100:.0f}%
- Detected Compliance: {analysis.get('compliance_requirements', [])}

USER'S DISCOVERY RESPONSES:
{discovery_response}

YOUR TASK: Create a comprehensive requirements specification.

ANALYZE THE RESPONSES:
1. **Extract Specific Requirements**: Pull out concrete technical requirements
2. **Identify Architecture Decisions**: Determine optimal AWS services and configurations
3. **Spot Missing Information**: What critical details are still unclear?
4. **Apply Best Practices**: Recommend improvements based on AWS Well-Architected Framework

CREATE A DETAILED SPECIFICATION:

```
REFINED ARCHITECTURE SPECIFICATION:

Core Technical Requirements:
- [Specific services, configurations, and parameters from responses]
- [Performance requirements with concrete numbers]
- [Integration points and data flows]

Recommended Architecture:
- [Primary AWS services with justification]
- [Architecture patterns and design decisions]
- [Security and compliance implementations]

Configuration Details:
- [Instance types, storage sizes, network configurations]
- [Auto-scaling policies and performance targets]
- [Monitoring, logging, and backup strategies]

Outstanding Questions:
- [Any remaining ambiguities that need clarification]
- [Trade-off decisions the user needs to make]
```

If there are still significant gaps, ask 1-2 targeted follow-up questions. Otherwise, confirm you're ready for architecture validation.
"""

    def _create_validation_prompt_from_refinement(self, original_description: str, analysis: dict, refined_spec: str) -> str:
        """Create a validation prompt based on refined specification."""
        
        return f"""
You are an expert AWS Solutions Architect performing final architecture validation.

ORIGINAL REQUEST: "{original_description}"

REFINED SPECIFICATION:
{refined_spec}

YOUR TASK: Perform comprehensive architecture review and validation.

VALIDATION FRAMEWORK:

1. **Architecture Soundness Review**:
   - Are all components properly integrated with clear data flows?
   - Are there any single points of failure or bottlenecks?
   - Is the solution scalable and maintainable?
   - Do service selections align with requirements?

2. **Security & Compliance Validation**:
   - Is data encrypted at rest and in transit appropriately?
   - Are IAM permissions following least privilege principle?
   - Are network security groups and NACLs properly configured?
   - Do compliance requirements have specific implementations?

3. **Operational Excellence Check**:
   - Is monitoring comprehensive with appropriate alarms?
   - Are backup and disaster recovery procedures defined?
   - Is the solution observable and debuggable?
   - Are operational runbooks and procedures considered?

4. **Performance & Cost Optimization**:
   - Are resources right-sized for expected load?
   - Are auto-scaling and performance optimizations in place?
   - Are there opportunities for cost savings (Reserved Instances, etc.)?
   - Is the architecture efficient for the use case?

5. **Reliability & Availability Assessment**:
   - Is the solution deployed across multiple AZs appropriately?
   - Are failure modes identified with mitigation strategies?
   - Are dependencies managed and failure isolation implemented?

PROVIDE YOUR VALIDATION REPORT:

```
ARCHITECTURE VALIDATION REPORT:

✅ VALIDATED COMPONENTS:
- [Architecture elements that meet all requirements]
- [Security implementations that are appropriate]
- [Performance configurations that are optimal]

⚠️ RECOMMENDATIONS FOR IMPROVEMENT:
- [Suggested enhancements with specific implementations]
- [Alternative approaches with trade-off analysis]
- [Cost optimization opportunities]

🚨 CRITICAL CONCERNS (if any):
- [Issues that must be addressed before implementation]
- [Security or compliance gaps that need resolution]

FINAL ARCHITECTURE SUMMARY:
- [Concise overview of the validated architecture]
- [Key services and their specific roles]
- [Critical configuration parameters and decisions]
- [Implementation priorities and dependencies]
```

Once validation is complete, confirm readiness for CloudFormation template generation.
"""

    def _create_generation_prompt(self, original_description: str, analysis: dict, validated_spec: str) -> str:
        """Create the final generation prompt for CloudFormation template creation."""
        
        architecture_type = analysis.get("architecture_type", "general")
        compliance_reqs = analysis.get("compliance_requirements", [])
        
        return f"""
You are an expert AWS Solutions Architect creating production-ready CloudFormation templates.

ORIGINAL REQUEST: "{original_description}"

VALIDATED ARCHITECTURE SPECIFICATION:
{validated_spec or "Use the original request and analysis for template generation."}

YOUR TASK: Create a comprehensive, production-ready CloudFormation template.

TEMPLATE GENERATION REQUIREMENTS:

1. **Template Structure Excellence**:
   - AWSTemplateFormatVersion: '2010-09-09'
   - Comprehensive Description explaining the architecture
   - Well-documented Parameters with validation constraints
   - Conditions for environment-specific logic where needed
   - Resources with proper dependencies and configurations
   - Meaningful Outputs for integration and reference

2. **AWS Best Practices Implementation**:
   - Use Ref and GetAtt functions appropriately
   - Implement proper resource dependencies with DependsOn
   - Include comprehensive resource tagging strategy
   - Use parameter validation, constraints, and allowed values
   - Implement condition logic for flexibility and reusability

3. **Security Implementation**:
   - Least privilege IAM policies with specific permissions
   - Enable encryption for all data stores and communications
   - Configure security groups with minimal necessary access
   - Include CloudTrail and comprehensive monitoring
   - Implement secrets management where applicable

4. **Operational Excellence**:
   - CloudWatch monitoring with appropriate alarms
   - Centralized logging with CloudWatch Logs
   - Automated backup strategies with retention policies
   - Disaster recovery considerations and implementations
   - Resource tagging for governance and cost management

5. **Architecture-Specific Requirements**:
"""

        # Add architecture-specific requirements
        if architecture_type == "web_application":
            prompt += """
   - Application Load Balancer with health checks
   - Auto Scaling Groups with appropriate policies
   - Database with Multi-AZ deployment and backups
   - CloudFront distribution for static content
   - Route53 for DNS management
"""
        elif architecture_type == "microservices":
            prompt += """
   - Container orchestration (ECS/EKS) with service discovery
   - API Gateway for external access and rate limiting
   - Inter-service communication security
   - Distributed tracing and centralized logging
   - Circuit breaker patterns and health checks
"""
        elif architecture_type == "data_processing":
            prompt += """
   - Data ingestion layer (Kinesis/SQS) with appropriate throughput
   - Processing compute (Lambda/EMR/Glue) with error handling
   - Data storage (S3/RDS/DynamoDB) with lifecycle policies
   - Data catalog and governance with AWS Glue
   - Monitoring and alerting for data quality
"""
        elif architecture_type == "serverless":
            prompt += """
   - Lambda functions with appropriate memory and timeout
   - API Gateway with throttling and caching
   - DynamoDB with on-demand or provisioned capacity
   - Event sources and triggers with error handling
   - X-Ray tracing for serverless observability
"""

        # Add compliance-specific requirements
        compliance_section = ""
        for compliance in compliance_reqs:
            if compliance == "hipaa":
                compliance_section += """
   - HIPAA Compliance Implementation:
     * All PHI data encrypted with customer-managed KMS keys
     * Comprehensive audit logging with CloudTrail
     * Access controls with role-based permissions
     * Network isolation with VPC and private subnets
     * Backup encryption and secure data handling
"""
            elif compliance == "pci_dss":
                compliance_section += """
   - PCI DSS Compliance Implementation:
     * Network segmentation for cardholder data environment
     * Strong encryption for data transmission and storage
     * Regular security testing with AWS Config rules
     * Access control measures with IAM and MFA
     * Vulnerability management with AWS Inspector
"""

        prompt += compliance_section + """

COMPREHENSIVE DELIVERABLES:

1. **Complete CloudFormation Template** (YAML format):
   - All resources properly configured and documented
   - Parameters with descriptions, constraints, and defaults
   - Conditions for environment-specific deployments
   - Outputs for key resource identifiers and endpoints

2. **Parameter File Template**:
   - Sample parameter values for different environments
   - Documentation of parameter purposes and constraints
   - Environment-specific configuration examples

3. **Deployment Documentation**:
   - Step-by-step deployment instructions
   - Prerequisites and dependency requirements
   - CLI commands for deployment and management
   - Validation procedures and health checks

4. **Architecture Documentation**:
   - Component relationship diagram (text-based description)
   - Data flow and integration points
   - Security model and access patterns
   - Scaling and performance characteristics

5. **Operational Procedures**:
   - Monitoring and alerting setup
   - Backup and recovery procedures
   - Troubleshooting common issues
   - Maintenance and update procedures

6. **Security and Compliance Summary**:
   - Security controls implementation
   - Compliance requirement mappings
   - Risk assessment and mitigation strategies
   - Audit and reporting capabilities

Generate the complete, production-ready CloudFormation solution now with all documentation and operational guidance.
"""
        
        return prompt