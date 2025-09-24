# CloudFormation Recovery MCP Server - Tool Analysis

## Overview

This MCP server has 6 tools that do two things: make real AWS API calls and generate expert prompts. Each tool combines actual CloudFormation operations with structured guidance for the LLM.

## Why Prompt Enhancement Matters

### Basic Request vs Enhanced Prompt

**Basic Request:**
```
"Generate a CloudFormation template for a web application"
```

**Enhanced Prompt:**
```
You are a CloudFormation expert. Create a production-ready web application template with:

ARCHITECTURE:
- Application Load Balancer with SSL termination
- Auto Scaling Group (2-10 instances) with health checks
- RDS Multi-AZ database with backup retention
- VPC with public/private subnets across 2 AZs
- Security groups with least privilege

SECURITY:
- Encryption at rest and in transit
- CloudTrail logging enabled
- VPC Flow Logs for network monitoring
- IAM roles with minimal permissions

OPERATIONS:
- CloudWatch alarms for key metrics
- SNS notifications for critical events
- Parameter validation and constraints
- Resource tagging strategy

OUTPUT:
- YAML format with comments
- Parameters section for customization
- Outputs section with resource identifiers
- Deployment instructions

VALIDATION:
- Validate resource dependencies
- Include rollback configuration
- Add stack policy for production protection
```

The enhanced prompt creates production-ready infrastructure. The basic request creates templates that need extensive manual work.

---

## Tool 1: enhanced_troubleshoot_cloudformation_stack

**What it does:** Analyzes CloudFormation stacks by collecting AWS data and generating troubleshooting guidance.

**AWS Operations:**

| What It Does | AWS API Calls | Data It Gets |
|--------------|---------------|--------------|
| Stack Analysis | describe_stacks, describe_stack_events | Status, events, parameters, outputs |
| Resource Discovery | describe_stack_resources | Resource states, failure reasons |
| Template Retrieval | get_template | Current template configuration |
| Log Collection | describe_log_groups, filter_log_events | Error logs, stack traces |
| CloudTrail Analysis | lookup_events | API call history, change tracking |
| Dependency Mapping | Template parsing + resource analysis | Resource relationships, circular dependencies |

**Code Implementation:**

```python
async def analyze_stack(self, stack_name: str, include_logs: bool = True, 
                       include_cloudtrail: bool = True, time_window_hours: int = 24) -> Dict[str, Any]:
    """
    Collects CloudFormation stack data from AWS APIs.
    
    Steps:
    1. Gets stack metadata, events, and resource states
    2. Downloads and parses CloudFormation template
    3. Searches CloudWatch logs for error patterns
    4. Gets CloudTrail events for change tracking
    5. Maps resource dependencies and identifies failures
    
    Returns structured data for LLM analysis.
    """
    # Make AWS API calls to collect data
    stack_data = await self._collect_stack_data(stack_name)
    cloudtrail_data = await self._collect_cloudtrail_events(stack_name, lookback_time, analysis_start_time)
    logs_data = await self._collect_cloudwatch_logs(stack_name, lookback_time, analysis_start_time)
    
    # Analyze the collected data
    failed_resources = await self._analyze_failed_resources(stack_data.get('failed_resources', []))
    dependency_analysis = await self._analyze_dependencies(stack_data.get('stack_template'))
    
    return {
        'raw_data': {
            'stack_info': stack_data,
            'cloudtrail_events': cloudtrail_data,
            'cloudwatch_logs': logs_data,
            'failed_resource_analysis': failed_resources,
            'dependency_analysis': dependency_analysis
        },
        'assessment': self._create_assessment(stack_name, stack_data)
    }

async def _collect_stack_data(self, stack_name: str) -> Dict[str, Any]:
    """Gets stack information from AWS APIs."""
    cfn_client = await self._get_cfn_client()
    
    # Get stack details
    stack_response = cfn_client.describe_stacks(StackName=stack_name)
    stack = stack_response['Stacks'][0]
    
    # Get stack events
    events_response = cfn_client.describe_stack_events(StackName=stack_name)
    events = events_response['StackEvents']
    
    # Get current template
    template_response = cfn_client.get_template(StackName=stack_name)
    template = template_response['TemplateBody']
    
    return {
        'stack_status': stack['StackStatus'],
        'stack_events': events,
        'stack_template': template,
        'failed_resources': [e for e in events if 'FAILED' in e.get('ResourceStatus', '')]
    }
```

**Prompt Enhancement:**

| Type | What It Generates |
|------|-------------------|
| Expert Context | "You are a CloudFormation troubleshooting expert with 10+ years of AWS experience..." |
| Step-by-Step Analysis | Investigation workflow with specific commands |
| Root Cause Guidance | Common failure patterns and how to diagnose them |
| Fix Recommendations | Specific solutions based on failure types |
| Prevention Tips | Best practices to avoid similar issues |

---

## Tool 2: generate_template_fixes

**What it does:** Finds and fixes CloudFormation template problems automatically.

**AWS Operations:**

| What It Does | How It Works | Validation Rules |
|--------------|--------------|------------------|
| Template Parsing | Custom YAML/JSON parser | Syntax validation, structure verification |
| Resource Validation | 50+ validation rules | Required properties, valid values, constraints |
| Dependency Analysis | Graph traversal algorithm | Circular dependencies, missing references |
| Security Analysis | Pattern matching + rules | Encryption, access controls, compliance |
| Fix Generation | Rule-based corrections | High-confidence automated fixes |

**Code Implementation:**

```python
def generate_fixes(self, template_content: str, auto_apply: bool = True) -> Dict[str, Any]:
    """
    Finds and fixes CloudFormation template problems.
    
    Steps:
    1. Parse template and validate syntax
    2. Run 50+ validation rules for common issues
    3. Generate specific fixes with confidence levels
    4. Apply high-confidence fixes automatically if requested
    5. Create backup and validate fixed template
    """
    # Parse template
    template = self._parse_template(template_content)
    
    # Run validation rules
    issues = []
    issues.extend(self._validate_resources(template))
    issues.extend(self._validate_dependencies(template))
    issues.extend(self._validate_security(template))
    issues.extend(self._validate_best_practices(template))
    
    # Generate fixes
    fixes = []
    for issue in issues:
        fix = self._generate_fix(issue, template)
        if fix:
            fixes.append(fix)
    
    # Apply high-confidence fixes if requested
    if auto_apply:
        fixed_template = self._apply_fixes(template, fixes)
        return {
            'original_template': template_content,
            'fixed_template': self._serialize_template(fixed_template),
            'fixes_applied': [f for f in fixes if f['confidence'] >= 0.8],
            'manual_fixes_needed': [f for f in fixes if f['confidence'] < 0.8]
        }
    
    return {'issues_found': issues, 'suggested_fixes': fixes}

def _validate_resources(self, template: Dict) -> List[Dict]:
    """Validates CloudFormation resources against AWS specs."""
    issues = []
    resources = template.get('Resources', {})
    
    for resource_name, resource_config in resources.items():
        resource_type = resource_config.get('Type')
        properties = resource_config.get('Properties', {})
        
        # Check required properties
        required_props = self.schema_manager.get_required_properties(resource_type)
        for prop in required_props:
            if prop not in properties:
                issues.append({
                    'type': 'missing_required_property',
                    'resource': resource_name,
                    'property': prop,
                    'severity': 'high',
                    'fix_confidence': 0.9
                })
    
    return issues
```

**Prompt Enhancement:**

| Type | What It Generates |
|------|-------------------|
| Fix Explanations | Why each fix is needed with AWS documentation links |
| Impact Analysis | What each fix changes and why it matters |
| Alternative Solutions | Multiple approaches for complex issues |
| Validation Commands | AWS CLI commands to verify fixes work |
| Best Practices | Industry standards and AWS Well-Architected principles |

---

## Tool 3: autonomous_fix_and_deploy_stack

**What it does:** Deploys CloudFormation stacks and automatically fixes problems that come up.

**AWS Operations:**

| What It Does | AWS API Calls | How It Works |
|--------------|---------------|--------------|
| Stack Deployment | create_stack, update_stack | Deployment with waiters |
| Failure Detection | describe_stack_events | Event analysis for failure patterns |
| Template Fixing | Template validation + correction | Automated fix application |
| Rollback Management | cancel_update_stack, delete_stack | Safe rollback on failures |
| Progress Monitoring | describe_stacks with polling | Real-time status tracking |

**Code Implementation:**

```python
async def fix_and_deploy(self, stack_name: str, template_content: str, max_iterations: int = 5) -> Dict[str, Any]:
    """
    Deploys CloudFormation stack and fixes problems automatically.
    
    Steps:
    1. Validate template and apply initial fixes
    2. Try deployment with real-time monitoring
    3. If it fails, analyze the failure
    4. Generate and apply targeted fixes
    5. Retry deployment until success or max iterations
    """
    iteration = 0
    current_template = template_content
    
    while iteration < max_iterations:
        iteration += 1
        
        # Apply fixes to current template
        fix_result = self.template_fixer.generate_fixes(current_template, auto_apply=True)
        current_template = fix_result.get('fixed_template', current_template)
        
        # Try deployment
        deploy_result = await self._deploy_stack(stack_name, current_template)
        
        if deploy_result['success']:
            return {
                'status': 'success',
                'iterations': iteration,
                'final_template': current_template,
                'deployment_result': deploy_result
            }
        
        # Analyze failure and prepare for next iteration
        failure_analysis = await self._analyze_deployment_failure(stack_name, deploy_result)
        current_template = await self._apply_failure_fixes(current_template, failure_analysis)
    
    return {'status': 'failed', 'max_iterations_reached': True}

async def _deploy_stack(self, stack_name: str, template_content: str) -> Dict[str, Any]:
    """Deploys CloudFormation stack with monitoring."""
    try:
        if self._stack_exists(stack_name):
            # Update existing stack
            response = self.cfn_client.update_stack(StackName=stack_name, TemplateBody=template_content)
            waiter = self.cfn_client.get_waiter('stack_update_complete')
        else:
            # Create new stack
            response = self.cfn_client.create_stack(StackName=stack_name, TemplateBody=template_content)
            waiter = self.cfn_client.get_waiter('stack_create_complete')
        
        # Wait for completion
        waiter.wait(StackName=stack_name, WaiterConfig={'Delay': 30, 'MaxAttempts': 120})
        
        return {'success': True, 'stack_id': response['StackId']}
        
    except Exception as e:
        # Collect failure details
        events = self._get_stack_events(stack_name)
        return {
            'success': False,
            'error': str(e),
            'failure_events': events,
            'failure_analysis': self._analyze_failure_events(events)
        }
```

**Prompt Enhancement:**

| Type | What It Generates |
|------|-------------------|
| Deployment Strategy | Step-by-step deployment guidance with checkpoints |
| Failure Recovery | Recovery procedures for different failure types |
| Monitoring Setup | CloudWatch alarms and notification configuration |
| Rollback Procedures | Safe rollback strategies with data protection |
| Operational Runbooks | Post-deployment validation and maintenance |

---

## Tool 4: analyze_template_structure

**What it does:** Analyzes CloudFormation templates for architecture review and optimization.

**AWS Operations:**

| What It Does | How It Works | What It Finds |
|--------------|--------------|---------------|
| Template Parsing | AST generation + validation | Structured template representation |
| Architecture Detection | Pattern matching algorithms | Architecture patterns |
| Security Scanning | Rule-based security analysis | Vulnerability assessment |
| Dependency Mapping | Graph analysis algorithms | Resource relationship visualization |
| Compliance Checking | Framework rule validation | HIPAA, PCI, SOX compliance status |

**Code Implementation:**

```python
def analyze_structure(self, template_content: str, analysis_focus: str = None) -> Dict[str, Any]:
    """
    Analyzes CloudFormation template structure.
    
    Steps:
    1. Parse template and build resource dependency graph
    2. Identify architecture patterns and anti-patterns
    3. Run security vulnerability scanning
    4. Check compliance framework alignment
    5. Generate optimization recommendations
    """
    template = self._parse_template(template_content)
    
    # Build analysis
    analysis = {
        'template_metadata': self._extract_metadata(template),
        'resource_analysis': self._analyze_resources(template),
        'dependency_graph': self._build_dependency_graph(template),
        'security_analysis': self._analyze_security(template),
        'architecture_patterns': self._detect_patterns(template),
        'compliance_status': self._check_compliance(template, analysis_focus)
    }
    
    return analysis

def _analyze_security(self, template: Dict) -> Dict[str, Any]:
    """Analyzes template for security issues."""
    security_issues = []
    resources = template.get('Resources', {})
    
    for name, resource in resources.items():
        resource_type = resource.get('Type')
        properties = resource.get('Properties', {})
        
        # Check encryption settings
        if resource_type == 'AWS::S3::Bucket':
            if not self._has_encryption_enabled(properties):
                security_issues.append({
                    'type': 'missing_encryption',
                    'resource': name,
                    'severity': 'high',
                    'recommendation': 'Enable S3 bucket encryption'
                })
        
        # Check IAM policies
        if resource_type == 'AWS::IAM::Role':
            policies = properties.get('Policies', [])
            for policy in policies:
                if self._has_wildcard_permissions(policy):
                    security_issues.append({
                        'type': 'overprivileged_iam',
                        'resource': name,
                        'severity': 'critical',
                        'recommendation': 'Apply principle of least privilege'
                    })
    
    return {'security_issues': security_issues, 'compliance_score': self._calculate_security_score(security_issues)}
```

**Prompt Enhancement:**

| Type | What It Generates |
|------|-------------------|
| Architecture Review | Expert architecture assessment with best practices |
| Security Recommendations | Security hardening guidance with implementations |
| Performance Optimization | Resource sizing and configuration optimization |
| Cost Optimization | Cost reduction opportunities with impact analysis |
| Compliance Guidance | Framework-specific compliance requirements |

---

## Tool 5: generate_cloudformation_template

**What it does:** Creates CloudFormation templates through smart requirements discovery.

**AWS Operations:**

| What It Does | How It Works | Intelligence Layer |
|--------------|--------------|-------------------|
| Requirements Analysis | NLP parsing + pattern matching | Architecture pattern detection |
| Template Generation | Rule-based template construction | Best practices integration |
| Validation | Schema validation + testing | Error checking |
| Documentation | Automated comment generation | Deployment guide creation |

**Code Implementation:**

```python
def generate_template(self, description: str, conversation_stage: str = "DISCOVERY") -> Dict[str, Any]:
    """
    Creates CloudFormation templates with expert guidance.
    
    Multi-stage process:
    1. DISCOVERY: Analyze requirements and ask clarifying questions
    2. REFINEMENT: Specify architecture details and trade-offs  
    3. VALIDATION: Review and validate final architecture
    4. GENERATION: Create production-ready template with documentation
    """
    
    if conversation_stage == "DISCOVERY":
        return self._generate_discovery_prompt(description)
    elif conversation_stage == "GENERATION":
        return self._generate_template_from_requirements(description)
    
    return self._generate_refinement_prompt(description, conversation_stage)

def _generate_discovery_prompt(self, description: str) -> Dict[str, Any]:
    """Creates smart discovery prompts for requirement gathering."""
    # Analyze user requirements
    detected_patterns = self._detect_architecture_patterns(description)
    missing_requirements = self._identify_missing_requirements(description, detected_patterns)
    
    # Generate targeted discovery questions
    discovery_questions = []
    for requirement in missing_requirements:
        questions = self._generate_questions_for_requirement(requirement)
        discovery_questions.extend(questions)
    
    return {
        'stage': 'DISCOVERY',
        'detected_patterns': detected_patterns,
        'discovery_prompt': self._create_discovery_prompt(description, discovery_questions),
        'next_stage': 'REFINEMENT'
    }
```

**Prompt Enhancement:**

| Type | What It Generates |
|------|-------------------|
| Requirements Discovery | Smart questioning to uncover missing requirements |
| Architecture Guidance | Expert recommendations for architecture patterns |
| Implementation Details | Specific configuration guidance with rationale |
| Deployment Strategy | Step-by-step deployment and validation procedures |
| Operational Excellence | Monitoring, alerting, and maintenance recommendations |

---

## Tool 6: cloudformation_best_practices_guide

**What it does:** Provides expert CloudFormation guidance for any infrastructure scenario.

**AWS Operations:**

| What It Does | How It Works | What It Provides |
|--------------|--------------|------------------|
| Issue Classification | Pattern matching algorithms | Category-specific recommendations |
| Best Practices Lookup | Curated knowledge database | Context-aware guidance |
| Solution Generation | Rule-based recommendation engine | Multiple solution approaches |
| Validation Guidance | Testing and verification procedures | Quality assurance steps |

**Code Implementation:**

```python
def generate_best_practices_guide(self, issue_description: str) -> Dict[str, Any]:
    """
    Generates expert CloudFormation best practices guidance.
    
    Steps:
    1. Classify the issue type and complexity
    2. Get relevant best practices from knowledge base
    3. Generate context-specific recommendations
    4. Provide validation and testing guidance
    """
    
    # Classify the issue for targeted guidance
    issue_classification = self._classify_issue(issue_description)
    
    # Get relevant best practices
    best_practices = self._get_best_practices_for_classification(issue_classification)
    
    # Generate guidance
    guidance = {
        'issue_analysis': issue_classification,
        'recommended_approaches': self._generate_solution_approaches(issue_classification),
        'implementation_guidance': self._create_implementation_guide(best_practices),
        'validation_procedures': self._generate_validation_steps(issue_classification),
        'expert_prompt': self._create_expert_guidance_prompt(issue_description, best_practices)
    }
    
    return guidance

def _classify_issue(self, description: str) -> Dict[str, Any]:
    """Classifies issues for targeted guidance."""
    classification = {
        'primary_category': None,
        'complexity_level': 'intermediate',
        'aws_services': [],
        'compliance_frameworks': [],
        'operational_impact': 'medium'
    }
    
    # Pattern matching for issue categorization
    if any(keyword in description.lower() for keyword in ['deploy', 'create', 'update']):
        classification['primary_category'] = 'deployment'
    elif any(keyword in description.lower() for keyword in ['security', 'iam', 'encryption']):
        classification['primary_category'] = 'security'
    elif any(keyword in description.lower() for keyword in ['performance', 'slow', 'timeout']):
        classification['primary_category'] = 'performance'
    
    return classification
```

**Prompt Enhancement:**

| Type | What It Generates |
|------|-------------------|
| Expert Context | "You are a CloudFormation architect with deep AWS expertise..." |
| Step-by-Step Guidance | Implementation procedures with checkpoints |
| Alternative Approaches | Multiple solution paths with trade-offs |
| Risk Assessment | Potential issues and mitigation strategies |
| Quality Assurance | Testing, validation, and monitoring recommendations |

---

## Summary

The CloudFormation Recovery MCP Server uses a hybrid approach:

• **AWS Operations (60-90% per tool)**: Real AWS API calls, data collection, template parsing, validation rules, and automated fixing
• **Prompt Enhancement (10-40% per tool)**: Expert-level guidance generation, structured workflows, and recommendations

This gives you both immediate technical capability and expert-level guidance that would normally require senior CloudFormation architects. It makes complex infrastructure management accessible while maintaining production-quality standards.
