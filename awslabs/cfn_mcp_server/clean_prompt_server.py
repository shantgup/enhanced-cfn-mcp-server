#!/usr/bin/env python3
"""
Clean CloudFormation Prompt Enhancement MCP Server

This server transforms basic user requests into expert-level prompts for Claude.
It focuses on ONLY three core capabilities:

1. Template Generation Enhancement - Transform "create X" into expert template guidance
2. Troubleshooting Enhancement - Transform "fix my stack" into comprehensive diagnostic workflow  
3. Fix and Retry Enhancement - Transform "retry deployment" into iterative fix strategy

The server does NOT try to compete with Claude's intelligence. Instead, it enhances
user prompts with expert AWS context, comprehensive diagnostic data, and systematic workflows.
"""

import argparse
import json
import traceback
import boto3
from typing import Dict, List, Any, Optional
from mcp.server.fastmcp import FastMCP
from pydantic import Field

# Import our clean prompt enhancement modules
from awslabs.cfn_mcp_server.template_generator_clean import TemplateGenerator
from awslabs.cfn_mcp_server.troubleshooting_enhancer_clean import TroubleshootingEnhancer
from awslabs.cfn_mcp_server.aws_client import get_aws_client, get_actual_region

# Initialize the MCP server
mcp = FastMCP("Clean CloudFormation Prompt Enhancement Server")

# Global instances
template_generator = None
troubleshooting_enhancer = None

def initialize_components():
    """Initialize the prompt enhancement components.
    
    Raises:
        RuntimeError: If critical components fail to initialize
    """
    global template_generator, troubleshooting_enhancer
    
    initialization_errors = []
    
    try:
        template_generator = TemplateGenerator()
        if not hasattr(template_generator, 'architecture_patterns'):
            initialization_errors.append("TemplateGenerator missing architecture patterns")
    except Exception as e:
        initialization_errors.append(f"TemplateGenerator initialization failed: {e}")
        template_generator = None
    
    try:
        troubleshooting_enhancer = TroubleshootingEnhancer()
        if not hasattr(troubleshooting_enhancer, 'error_patterns'):
            initialization_errors.append("TroubleshootingEnhancer missing error patterns")
    except Exception as e:
        initialization_errors.append(f"TroubleshootingEnhancer initialization failed: {e}")
        troubleshooting_enhancer = None
    
    if initialization_errors:
        error_msg = "; ".join(initialization_errors)
        raise RuntimeError(f"Component initialization failed: {error_msg}")
    
    print("✅ Prompt enhancement components initialized successfully")

def is_components_initialized() -> bool:
    """Check if all components are properly initialized."""
    return (template_generator is not None and 
            troubleshooting_enhancer is not None and
            hasattr(template_generator, 'architecture_patterns') and
            hasattr(troubleshooting_enhancer, 'error_patterns'))

# =============================================================================
# CORE PROMPT ENHANCEMENT TOOLS (ONLY 3)
# =============================================================================

@mcp.tool()
def generate_cloudformation_template_enhancement(
    description: str = Field(description="Natural language description of infrastructure to enhance"),
    region: str = Field(default="us-east-1", description="AWS region for the template"),
    template_format: str = Field(default="YAML", description="Output format (YAML or JSON)"),
    save_to_file: Optional[str] = Field(default=None, description="Optional file path to save enhanced prompt")
) -> Dict[str, Any]:
    """
    Transform basic template requests into expert-level prompts for Claude.
    
    This tool takes a simple request like "create a web app" and transforms it into
    a comprehensive expert prompt with architecture requirements, security best practices,
    compliance considerations, and implementation guidance.
    
    Example transformation:
    Input: "Create a web app"
    Output: 3000+ character expert prompt with architecture patterns, security requirements,
            operational excellence guidelines, and comprehensive implementation checklists.
    """
    try:
        if not template_generator:
            return {
                "success": False,
                "error": "Template generator not initialized",
                "expert_prompt_for_claude": f"Create a CloudFormation template for: {description}"
            }
        # Check if components are initialized
        if not is_components_initialized():
            return {
                "success": False,
                "error": "Template generator components not properly initialized",
                "enhanced_prompt": "",
                "conversation_stage": "ERROR"
            }
        
        # Generate the enhanced expert prompt
        result = template_generator.generate_enhanced_prompt(
            description=description,
            region=region,
            template_format=template_format
        )
        
        # Save to file if requested
        if save_to_file and result.get("success"):
            try:
                with open(save_to_file, 'w') as f:
                    f.write(result.get("expert_prompt_for_claude", ""))
                result["saved_to_file"] = save_to_file
            except Exception as e:
                result["file_save_error"] = str(e)
        
        return result
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "traceback": traceback.format_exc(),
            "expert_prompt_for_claude": f"Create a CloudFormation template for: {description}",
            "fallback_guidance": "Please create a comprehensive CloudFormation template with security best practices and monitoring."
        }

@mcp.tool()
def troubleshoot_cloudformation_stack_enhancement(
    stack_name: str = Field(description="Name of the CloudFormation stack to troubleshoot"),
    region: Optional[str] = Field(default=None, description="AWS region (auto-detected if not provided)"),
    include_logs: bool = Field(default=True, description="Include CloudWatch logs analysis"),
    include_cloudtrail: bool = Field(default=True, description="Include CloudTrail events analysis"),
    time_window_hours: int = Field(default=24, description="Time window for log/event analysis"),
    symptoms_description: Optional[str] = Field(default=None, description="Description of observed symptoms")
) -> Dict[str, Any]:
    """
    Transform basic troubleshooting requests into comprehensive diagnostic workflows.
    
    This tool takes a simple request like "fix my stack" and transforms it into a systematic
    troubleshooting workflow with:
    - Real AWS diagnostic data collection (CloudTrail, stack events, template analysis)
    - Resource configuration analysis via describe API calls
    - CloudWatch logs analysis where needed
    - Root cause analysis and correlation
    - Step-by-step resolution procedures
    - Validation checklists and rollback plans
    
    Example transformation:
    Input: "My stack failed"
    Output: Comprehensive diagnostic report with actual AWS data, root cause analysis,
            and expert-level troubleshooting workflow for Claude to execute.
    """
    try:
        if not troubleshooting_enhancer:
            return {
                "success": False,
                "error": "Troubleshooting enhancer not initialized",
                "expert_prompt_for_claude": f"Please troubleshoot CloudFormation stack: {stack_name}"
            }
        
        # Get actual region
        actual_region = get_actual_region(region)
        
        # Generate comprehensive troubleshooting enhancement
        result = troubleshooting_enhancer.enhance_troubleshooting_request(
            stack_name=stack_name,
            region=actual_region,
            include_logs=include_logs,
            include_cloudtrail=include_cloudtrail,
            time_window_hours=time_window_hours,
            symptoms_description=symptoms_description
        )
        
        return result
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "traceback": traceback.format_exc(),
            "expert_prompt_for_claude": f"Please troubleshoot CloudFormation stack '{stack_name}' with comprehensive analysis.",
            "fallback_guidance": "Analyze stack events, check resource status, review CloudWatch logs, and provide systematic resolution steps."
        }

@mcp.tool()
def fix_and_retry_cloudformation_enhancement(
    stack_name: str = Field(description="Name of the stack to fix and retry"),
    region: Optional[str] = Field(default=None, description="AWS region (auto-detected if not provided)"),
    max_iterations: int = Field(default=5, description="Maximum fix-retry iterations"),
    auto_apply_fixes: bool = Field(default=True, description="Whether to automatically apply high-confidence fixes"),
    backup_template: bool = Field(default=True, description="Whether to backup original template"),
    failure_context: Optional[str] = Field(default=None, description="Context about previous failures")
) -> Dict[str, Any]:
    """
    Transform basic retry requests into comprehensive iterative fix strategies.
    
    This tool takes a simple request like "retry my deployment" and transforms it into
    a systematic fix-and-retry workflow with:
    - Analysis of previous failure patterns
    - Iterative fixing strategies with confidence levels
    - Template backup and version control
    - Validation checklists between iterations
    - Rollback plans and safety measures
    - Progress tracking and success criteria
    
    Example transformation:
    Input: "Retry my stack deployment"
    Output: Comprehensive iterative strategy with failure analysis, systematic fixes,
            validation procedures, and expert guidance for Claude to execute multiple iterations.
    """
    try:
        if not troubleshooting_enhancer:
            return {
                "success": False,
                "error": "Troubleshooting enhancer not initialized",
                "expert_prompt_for_claude": f"Please fix and retry CloudFormation stack: {stack_name}"
            }
        
        # Get actual region
        actual_region = get_actual_region(region)
        
        # First, get comprehensive troubleshooting data
        troubleshooting_result = troubleshooting_enhancer.enhance_troubleshooting_request(
            stack_name=stack_name,
            region=actual_region,
            include_logs=True,
            include_cloudtrail=True,
            time_window_hours=48,  # Longer window for retry analysis
            symptoms_description=failure_context
        )
        
        # Generate fix-and-retry enhancement based on troubleshooting data
        fix_retry_enhancement = generate_fix_retry_enhancement(
            stack_name=stack_name,
            region=actual_region,
            max_iterations=max_iterations,
            auto_apply_fixes=auto_apply_fixes,
            backup_template=backup_template,
            troubleshooting_data=troubleshooting_result,
            failure_context=failure_context
        )
        
        return fix_retry_enhancement
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "traceback": traceback.format_exc(),
            "expert_prompt_for_claude": f"Please fix and retry CloudFormation stack '{stack_name}' with iterative approach.",
            "fallback_guidance": "Analyze failures, apply fixes systematically, validate between iterations, and retry with improvements."
        }

# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def generate_fix_retry_enhancement(
    stack_name: str,
    region: str,
    max_iterations: int,
    auto_apply_fixes: bool,
    backup_template: bool,
    troubleshooting_data: Dict[str, Any],
    failure_context: Optional[str]
) -> Dict[str, Any]:
    """Generate comprehensive fix-and-retry enhancement prompt."""
    
    # Extract key information from troubleshooting data
    stack_status = troubleshooting_data.get("raw_data", {}).get("stack_info", {}).get("stack_status")
    failed_events = troubleshooting_data.get("raw_data", {}).get("stack_info", {}).get("failed_events", [])
    template_content = troubleshooting_data.get("raw_data", {}).get("stack_info", {}).get("stack_template")
    
    # Build comprehensive fix-retry prompt
    expert_prompt = f"""

You are an expert AWS Solutions Architect specializing in CloudFormation troubleshooting and iterative deployment strategies. 

ORIGINAL REQUEST: Fix and retry CloudFormation stack '{stack_name}' until successful deployment.

CURRENT SITUATION ANALYSIS:
- Stack Name: {stack_name}
- Region: {region}
- Current Status: {stack_status or 'Unknown'}
- Failed Events Count: {len(failed_events)}
- Template Available: {'Yes' if template_content else 'No'}
- Failure Context: {failure_context or 'Not provided'}

COMPREHENSIVE TROUBLESHOOTING DATA:
{json.dumps(troubleshooting_data.get("raw_data", {}), indent=2, default=str)}

ITERATIVE FIX-AND-RETRY STRATEGY:

Please implement a systematic fix-and-retry approach with the following phases:

PHASE 1: FAILURE ANALYSIS
- Analyze all failed events and identify root causes
- Categorize failures by type (permissions, resources, dependencies, etc.)
- Prioritize fixes by impact and confidence level
- Identify any circular dependencies or architectural issues

PHASE 2: TEMPLATE PREPARATION
{'- Create backup of original template before modifications' if backup_template else '- Proceed without template backup (as requested)'}
- Apply high-confidence fixes first
- Validate template syntax and logic
- Check for common CloudFormation pitfalls

PHASE 3: ITERATIVE DEPLOYMENT (Max {max_iterations} iterations)
For each iteration:
1. Apply next set of fixes based on priority
2. Validate template changes
3. Deploy with appropriate parameters and capabilities
4. Monitor deployment progress in real-time
5. If failure occurs:
   - Capture new failure data
   - Analyze what changed
   - Adjust strategy for next iteration
6. If success: Validate all resources are healthy

PHASE 4: VALIDATION AND MONITORING
- Verify all resources are in expected state
- Test functionality where possible
- Set up monitoring and alerting
- Document what was fixed for future reference

FIX STRATEGY CONFIGURATION:
- Auto-apply high-confidence fixes: {'Yes' if auto_apply_fixes else 'No'}
- Maximum iterations allowed: {max_iterations}
- Backup strategy: {'Enabled' if backup_template else 'Disabled'}

SAFETY MEASURES:
- Always validate template syntax before deployment
- Monitor resource costs during deployment
- Have rollback plan ready for each iteration
- Stop if iterations exceed maximum or if critical errors occur

EXPECTED DELIVERABLES:
1. Detailed failure analysis with root causes
2. Prioritized fix list with confidence levels
3. Step-by-step iteration plan
4. Template modifications (if needed)
5. Deployment commands with proper parameters
6. Validation checklist for each iteration
7. Final success confirmation and monitoring setup

Please execute this comprehensive fix-and-retry strategy systematically, providing detailed feedback at each phase.

"""

    return {
        "success": True,
        "expert_prompt_for_claude": expert_prompt,
        "original_request": f"Fix and retry stack {stack_name}",
        "enhancement_type": "fix_and_retry_strategy",
        "configuration": {
            "max_iterations": max_iterations,
            "auto_apply_fixes": auto_apply_fixes,
            "backup_template": backup_template,
            "region": region
        },
        "troubleshooting_data_included": True,
        "strategy_phases": [
            "Failure Analysis",
            "Template Preparation", 
            "Iterative Deployment",
            "Validation and Monitoring"
        ],
        "safety_measures": [
            "Template syntax validation",
            "Cost monitoring",
            "Rollback planning",
            "Iteration limits"
        ]
    }

# =============================================================================
# SERVER INITIALIZATION
# =============================================================================

def main():
    """Main entry point for the clean prompt enhancement server."""
    parser = argparse.ArgumentParser(description="Clean CloudFormation Prompt Enhancement MCP Server")
    parser.add_argument("--readonly", action="store_true", help="Run in read-only mode")
    args = parser.parse_args()
    
    # Initialize components
    initialize_components()
    
    print("🚀 Clean CloudFormation Prompt Enhancement Server")
    print("=" * 60)
    print("✨ Core Capabilities:")
    print("  1. Template Generation Enhancement")
    print("  2. Troubleshooting Enhancement") 
    print("  3. Fix and Retry Enhancement")
    print("=" * 60)
    print("🎯 Mission: Transform basic requests into expert-level prompts")
    print("💡 Approach: Enhance prompts, don't compete with Claude's intelligence")
    
    if args.readonly:
        print("🔒 Running in read-only mode")
    
    # Run the server
    mcp.run()

if __name__ == "__main__":
    main()
