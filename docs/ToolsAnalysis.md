# CloudFormation Recovery MCP Server - Tool Analysis

## Overview

This MCP server provides 6 CloudFormation tools. Each tool does AWS operations and generates structured prompts to guide the LLM.

## How Prompt Enhancement Works

### Basic Request vs Structured Prompt

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

The structured prompt produces production-ready infrastructure. The basic request needs extensive manual work.

---

## Tool 1: enhanced_troubleshoot_cloudformation_stack

**What it does:** Analyzes CloudFormation stacks and generates troubleshooting guidance.

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
# From server.py:1280 - Tool entry point
async def enhanced_troubleshoot_cloudformation_stack(stack_name: str, region: str = None, ...):
    troubleshooter = EnhancedCloudFormationTroubleshooter(get_actual_region(region))
    result = await troubleshooter.comprehensive_analysis(
        stack_name=stack_name,
        include_template_analysis=include_template_analysis,
        include_logs=include_logs,
        include_cloudtrail=include_cloudtrail,
        time_window_hours=time_window_hours,
        symptoms_description=symptoms_description
    )
    return result

# From enhanced_troubleshooter.py:34 - Main analysis method
async def comprehensive_analysis(self, stack_name: str, include_template_analysis: bool = True, ...):
    # Get base AWS data (stack info, events, template, logs, CloudTrail)
    base_analysis = await self.analyze_stack(
        stack_name=stack_name,
        include_logs=include_logs,
        include_cloudtrail=include_cloudtrail,
        time_window_hours=time_window_hours
    )
    
    # Enhanced analysis with template deep-dive
    enhanced_analysis = {
        'base_analysis': base_analysis,
        'template_analysis': {},
        'issue_correlation': {},
        'fix_recommendations': [],
        'autonomous_fix_plan': {},
        'deployment_readiness': {}
    }
    
    # Analyze template if requested
    if include_template_analysis and stack_template:
        template_analysis = self.template_analyzer.analyze_template(stack_template)
        enhanced_analysis['template_analysis'] = template_analysis
        
        # Correlate template issues with stack failures
        correlation = self.template_analyzer.correlate_with_stack_events(
            template_analysis, base_analysis.get('stack_events', [])
        )
        enhanced_analysis['issue_correlation'] = correlation
    
    # Generate fix recommendations
    fix_recommendations = self._generate_comprehensive_fix_recommendations(enhanced_analysis)
    enhanced_analysis['fix_recommendations'] = fix_recommendations
    
    return enhanced_analysis
```

**Implementation Files:**
- `server.py:1280` - Tool definition and parameter handling
- `enhanced_troubleshooter.py:34` - Main analysis orchestration
- `troubleshooter.py:90` - Base AWS API calls (describe_stacks, get_template, etc.)
- `template_analyzer.py` - Template validation with 50+ rules
- `template_fixer.py` - Automated fix generation
- `aws_client.py` - AWS service clients and error handling

**What the prompts add:**

| Component | Purpose |
|-----------|---------|
| Expert Context | Sets up troubleshooting methodology and approach |
| Investigation Steps | Specific commands and checks to run |
| Failure Patterns | Common issues and how to spot them |
| Fix Instructions | Step-by-step solutions for each problem type |
| Prevention Guide | Configuration changes to avoid repeat issues |

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
# From server.py:1501 - Tool entry point
async def generate_template_fixes(template_content: str, auto_apply: bool = True, max_fixes: int = 50):
    # Parse template using enhanced CloudFormation parser
    template = parse_cloudformation_template(template_content)
    
    # Analyze template for issues
    analyzer = TemplateAnalyzer()
    analysis = analyzer.analyze_template(template)
    
    # Generate fixes using TemplateFixer
    fixer = TemplateFixer()
    fixes = fixer.generate_fixes(analysis, template, max_fixes)
    
    # Apply high-confidence fixes if requested
    if auto_apply:
        applied_fixes = []
        for fix in fixes:
            if fix.get('confidence', 0) >= 0.8:  # High confidence threshold
                template = fixer.apply_fix(template, fix)
                applied_fixes.append(fix)
        
        return {
            'success': True,
            'original_template': template_content,
            'fixed_template': serialize_template(template),
            'fixes_applied': applied_fixes,
            'manual_fixes_needed': [f for f in fixes if f.get('confidence', 0) < 0.8]
        }
    
    return {'success': True, 'issues_found': analysis.get('issues', []), 'suggested_fixes': fixes}
```

**Implementation Files:**
- `server.py:1501` - Tool definition and orchestration
- `template_analyzer.py` - Template parsing and issue detection (50+ validation rules)
- `template_fixer.py` - Fix generation and application logic
- `cloudformation_yaml.py` - Enhanced CloudFormation YAML/JSON parser

**What the prompts add:**

| Component | Purpose |
|-----------|---------|
| Fix Explanations | Why each fix is needed with AWS documentation links |
| Impact Analysis | What each fix changes and potential side effects |
| Alternative Solutions | Multiple approaches for complex issues |
| Validation Steps | AWS CLI commands to verify fixes work |
| Best Practices | Configuration standards and compliance requirements |

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
# From server.py:1307 - Tool entry point
async def autonomous_fix_and_deploy_stack(stack_name: str, region: str = None, 
                                        auto_apply_fixes: bool = True, max_iterations: int = 5, ...):
    troubleshooter = EnhancedCloudFormationTroubleshooter(get_actual_region(region))
    result = await troubleshooter.fix_and_deploy(
        stack_name=stack_name,
        auto_apply_fixes=auto_apply_fixes,
        max_iterations=max_iterations,
        parameters=parameters,
        capabilities=capabilities,
        tags=tags
    )
    return result

# From enhanced_troubleshooter.py - Main deployment loop
async def fix_and_deploy(self, stack_name: str, max_iterations: int = 5, ...):
    iteration = 0
    
    while iteration < max_iterations:
        iteration += 1
        
        # Get current template (from existing stack or provided)
        current_template = await self._get_stack_template(stack_name)
        
        # Apply template fixes
        if auto_apply_fixes:
            fix_result = await self.template_fixer.generate_fixes(current_template, auto_apply=True)
            current_template = fix_result.get('fixed_template', current_template)
        
        # Try deployment
        deploy_result = await self._deploy_stack_with_monitoring(stack_name, current_template, parameters, capabilities, tags)
        
        if deploy_result['success']:
            return {
                'status': 'success',
                'iterations': iteration,
                'final_template': current_template,
                'deployment_result': deploy_result
            }
        
        # Analyze failure and prepare for next iteration
        failure_analysis = await self._analyze_deployment_failure(stack_name, deploy_result)
        # Continue to next iteration with failure-specific fixes
    
    return {'status': 'failed', 'max_iterations_reached': True, 'iterations': iteration}
```

**Implementation Files:**
- `server.py:1307` - Tool definition and parameter handling
- `enhanced_troubleshooter.py` - Main deployment orchestration and retry logic
- `autonomous_deployer.py` - Deployment monitoring and failure analysis
- `template_fixer.py` - Failure-specific fix generation

**What the prompts add:**

| Component | Purpose |
|-----------|---------|
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
# From server.py:1393 - Tool entry point  
async def analyze_template_structure(template_content: str, region: str = None, analysis_focus: str = None):
    analyzer = TemplateAnalyzer()
    analysis = analyzer.analyze_template(parse_cloudformation_template(template_content))
    
    # Focus analysis based on request
    if analysis_focus == "security":
        analysis['security_analysis'] = analyzer.analyze_security(template)
    elif analysis_focus == "compliance":
        analysis['compliance_analysis'] = analyzer.check_compliance(template, analysis_focus)
    
    return analysis

# From template_analyzer.py - Main analysis method
def analyze_template(self, template: Dict) -> Dict[str, Any]:
    return {
        'template_metadata': self._extract_metadata(template),
        'resource_analysis': self._analyze_resources(template),
        'dependency_graph': self._build_dependency_graph(template),
        'security_analysis': self._analyze_security(template),
        'architecture_patterns': self._detect_patterns(template),
        'best_practices_compliance': self._check_best_practices(template)
    }

def _analyze_security(self, template: Dict) -> Dict[str, Any]:
    security_issues = []
    resources = template.get('Resources', {})
    
    for name, resource in resources.items():
        resource_type = resource.get('Type')
        properties = resource.get('Properties', {})
        
        # Check encryption, IAM policies, network security, etc.
        issues = self._check_resource_security(resource_type, properties, name)
        security_issues.extend(issues)
    
    return {'security_issues': security_issues, 'compliance_score': self._calculate_security_score(security_issues)}
```

**Implementation Files:**
- `server.py:1393` - Tool definition and analysis focus routing
- `template_analyzer.py` - Template parsing, security analysis, compliance checking
- `dependency_analyzer.py` - Resource dependency mapping and circular dependency detection
- `security_analyzer.py` - Security vulnerability detection with 30+ security rules

**What the prompts add:**

| Component | Purpose |
|-----------|---------|
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
# From server.py:338 - Tool entry point
async def generate_cloudformation_template(description: str, conversation_stage: str = "DISCOVERY", 
                                         region: str = None, template_format: str = "YAML", ...):
    generator = CloudFormationTemplateGenerator(get_actual_region(region))
    
    if conversation_stage == "DISCOVERY":
        return generator.generate_discovery_prompt(description)
    elif conversation_stage == "GENERATION":
        return generator.generate_template_from_requirements(description, template_format, save_to_file)
    else:
        return generator.generate_refinement_prompt(description, conversation_stage, previous_response)

# From template_generator.py - Multi-stage generation
def generate_discovery_prompt(self, description: str) -> Dict[str, Any]:
    # Analyze user requirements using NLP
    detected_patterns = self._detect_architecture_patterns(description)
    missing_requirements = self._identify_missing_requirements(description, detected_patterns)
    
    return {
        'conversation_stage': 'DISCOVERY',
        'detected_patterns': detected_patterns,
        'clarifying_questions': self._generate_clarifying_questions(missing_requirements),
        'expert_prompt': self._create_discovery_prompt(description, detected_patterns)
    }

def generate_template_from_requirements(self, requirements: str, format: str = "YAML") -> Dict[str, Any]:
    # Parse finalized requirements
    parsed_requirements = self._parse_requirements(requirements)
    
    # Generate template using rule-based construction
    template = self._build_template_from_requirements(parsed_requirements)
    
    # Add best practices and documentation
    template = self._apply_best_practices(template)
    documentation = self._generate_documentation(template, parsed_requirements)
    
    return {
        'template': self._serialize_template(template, format),
        'documentation': documentation,
        'deployment_guide': self._create_deployment_guide(template)
    }
```

**Implementation Files:**
- `server.py:338` - Tool definition and conversation stage routing
- `template_generator.py` - Multi-stage template generation with NLP analysis
- `requirements_parser.py` - Natural language requirement parsing and pattern detection
- `template_builder.py` - Rule-based CloudFormation template construction

**What the prompts add:**

| Component | Purpose |
|-----------|---------|
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
# From server.py:1600 - Tool entry point
async def cloudformation_best_practices_guide(issue_description: str):
    guide_generator = BestPracticesGuideGenerator()
    return guide_generator.generate_guidance(issue_description)

# From best_practices_generator.py - Main guidance generation
def generate_guidance(self, issue_description: str) -> Dict[str, Any]:
    # Classify the issue for targeted guidance
    issue_classification = self._classify_issue(issue_description)
    
    # Get relevant best practices from knowledge base
    best_practices = self._get_best_practices_for_classification(issue_classification)
    
    # Generate structured guidance
    return {
        'issue_analysis': issue_classification,
        'recommended_approaches': self._generate_solution_approaches(issue_classification),
        'implementation_guidance': self._create_implementation_guide(best_practices),
        'validation_procedures': self._generate_validation_steps(issue_classification),
        'expert_prompt': self._create_expert_guidance_prompt(issue_description, best_practices)
    }

def _classify_issue(self, description: str) -> Dict[str, Any]:
    # Pattern matching for issue categorization
    classification = {'primary_category': None, 'complexity_level': 'intermediate', 'aws_services': []}
    
    if any(keyword in description.lower() for keyword in ['deploy', 'create', 'update']):
        classification['primary_category'] = 'deployment'
    elif any(keyword in description.lower() for keyword in ['security', 'iam', 'encryption']):
        classification['primary_category'] = 'security'
    elif any(keyword in description.lower() for keyword in ['performance', 'slow', 'timeout']):
        classification['primary_category'] = 'performance'
    
    return classification
```

**Implementation Files:**
- `server.py:1600` - Tool definition and issue routing
- `best_practices_generator.py` - Issue classification and guidance generation
- `knowledge_base.py` - Curated best practices database with 200+ patterns
- `solution_generator.py` - Context-aware solution recommendation engine

**What the prompts add:**

| Component | Purpose |
|-----------|---------|
| Expert Context | Sets up CloudFormation architecture expertise and methodology |
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
