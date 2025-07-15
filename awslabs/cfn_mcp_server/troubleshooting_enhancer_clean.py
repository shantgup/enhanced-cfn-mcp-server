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
Clean Troubleshooting Enhancer - Pure Prompt Enhancement

This module transforms basic troubleshooting requests into comprehensive expert prompts
that guide Claude through systematic CloudFormation troubleshooting workflows.

Key Focus:
- Gather comprehensive diagnostic data from AWS
- Create expert-level troubleshooting prompts
- Provide specific CLI commands and workflows
- Include best practices and systematic approaches
"""

import boto3
import json
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from awslabs.cfn_mcp_server.aws_client import get_aws_client, get_actual_region

class TroubleshootingEnhancer:
    """
    Enhances basic troubleshooting requests into comprehensive expert prompts.
    
    This class gathers real AWS data and creates detailed prompts that help Claude
    provide superior troubleshooting guidance with specific context and commands.
    """
    
    def __init__(self):
        """Initialize the troubleshooting enhancer."""
        self.cloudformation_client = None
        self.cloudtrail_client = None
        self.logs_client = None
        
    def _get_clients(self, region: Optional[str] = None):
        """Get AWS clients for the specified region."""
        actual_region = get_actual_region(region)
        
        if not self.cloudformation_client:
            self.cloudformation_client = get_aws_client('cloudformation', actual_region)
            self.cloudtrail_client = get_aws_client('cloudtrail', actual_region)
            self.logs_client = get_aws_client('logs', actual_region)
    
    def create_enhanced_troubleshooting_prompt(
        self,
        stack_name: str,
        region: Optional[str] = None,
        include_logs: bool = True,
        include_cloudtrail: bool = True,
        max_events: int = 50,
        time_window_hours: int = 24,
        symptoms_description: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Create an enhanced troubleshooting prompt with comprehensive AWS data.
        
        This method gathers real data from AWS and creates expert-level prompts
        that guide Claude through systematic troubleshooting.
        """
        try:
            self._get_clients(region)
            
            # Gather comprehensive troubleshooting data
            stack_data = self._gather_stack_data(stack_name, max_events)
            cloudtrail_data = self._gather_cloudtrail_data(stack_name, time_window_hours) if include_cloudtrail else {}
            logs_data = self._gather_logs_data(stack_name, time_window_hours) if include_logs else {}
            
            # Analyze the data to categorize issues
            issue_analysis = self._analyze_issues(stack_data, cloudtrail_data, logs_data)
            
            # Create the enhanced expert prompt
            expert_prompt = self._create_expert_troubleshooting_prompt(
                stack_name=stack_name,
                region=region,
                stack_data=stack_data,
                cloudtrail_data=cloudtrail_data,
                logs_data=logs_data,
                issue_analysis=issue_analysis,
                symptoms_description=symptoms_description
            )
            
            return {
                "expert_prompt_for_claude": expert_prompt,
                "stack_analysis": issue_analysis,
                "diagnostic_data": {
                    "stack_events_count": len(stack_data.get("events", [])),
                    "failed_resources_count": len(stack_data.get("failed_resources", [])),
                    "cloudtrail_events_count": len(cloudtrail_data.get("events", [])),
                    "log_errors_count": len(logs_data.get("error_logs", []))
                },
                "troubleshooting_workflow": self._create_troubleshooting_workflow(stack_name, issue_analysis),
                "cli_commands": self._generate_cli_commands(stack_name, region, issue_analysis),
                "next_steps": self._generate_next_steps(issue_analysis)
            }
            
        except Exception as e:
            # Fallback to basic prompt if data gathering fails
            return self._create_fallback_prompt(stack_name, region, symptoms_description, str(e))
    
    def _gather_stack_data(self, stack_name: str, max_events: int) -> Dict[str, Any]:
        """Gather comprehensive CloudFormation stack data."""
        try:
            # Get stack information
            stacks_response = self.cloudformation_client.describe_stacks(StackName=stack_name)
            stack = stacks_response['Stacks'][0] if stacks_response['Stacks'] else None
            
            # Get stack events
            events_response = self.cloudformation_client.describe_stack_events(
                StackName=stack_name,
                MaxItems=max_events
            )
            events = events_response.get('StackEvents', [])
            
            # Get stack resources
            try:
                resources_response = self.cloudformation_client.describe_stack_resources(StackName=stack_name)
                resources = resources_response.get('StackResources', [])
            except:
                resources = []
            
            # Get template
            try:
                template_response = self.cloudformation_client.get_template(StackName=stack_name)
                template = template_response.get('TemplateBody', {})
            except:
                template = {}
            
            # Identify failed resources and events
            failed_events = [e for e in events if 'FAILED' in e.get('ResourceStatus', '')]
            failed_resources = [r for r in resources if 'FAILED' in r.get('ResourceStatus', '')]
            
            return {
                "stack": stack,
                "events": events,
                "resources": resources,
                "template": template,
                "failed_events": failed_events,
                "failed_resources": failed_resources,
                "stack_status": stack.get('StackStatus') if stack else 'NOT_FOUND'
            }
            
        except Exception as e:
            return {"error": str(e), "stack_status": "ERROR"}
    
    def _gather_cloudtrail_data(self, stack_name: str, time_window_hours: int) -> Dict[str, Any]:
        """Gather relevant CloudTrail events for troubleshooting."""
        try:
            end_time = datetime.utcnow()
            start_time = end_time - timedelta(hours=time_window_hours)
            
            # Look for CloudFormation API calls related to this stack
            response = self.cloudtrail_client.lookup_events(
                LookupAttributes=[
                    {
                        'AttributeKey': 'ResourceName',
                        'AttributeValue': stack_name
                    }
                ],
                StartTime=start_time,
                EndTime=end_time,
                MaxItems=100
            )
            
            events = response.get('Events', [])
            error_events = [e for e in events if e.get('ErrorCode') or e.get('ErrorMessage')]
            
            return {
                "events": events,
                "error_events": error_events,
                "time_window": f"{start_time} to {end_time}"
            }
            
        except Exception as e:
            return {"error": str(e)}
    
    def _gather_logs_data(self, stack_name: str, time_window_hours: int) -> Dict[str, Any]:
        """Gather relevant CloudWatch logs for troubleshooting."""
        try:
            # Look for log groups related to the stack
            log_groups_response = self.logs_client.describe_log_groups(
                logGroupNamePrefix=f'/aws/cloudformation/{stack_name}'
            )
            
            log_groups = log_groups_response.get('logGroups', [])
            error_logs = []
            
            # Search for error patterns in recent logs
            end_time = int(datetime.utcnow().timestamp() * 1000)
            start_time = int((datetime.utcnow() - timedelta(hours=time_window_hours)).timestamp() * 1000)
            
            for log_group in log_groups[:3]:  # Limit to first 3 log groups
                try:
                    events_response = self.logs_client.filter_log_events(
                        logGroupName=log_group['logGroupName'],
                        startTime=start_time,
                        endTime=end_time,
                        filterPattern='ERROR FAILED Exception',
                        limit=50
                    )
                    
                    error_logs.extend(events_response.get('events', []))
                except:
                    continue
            
            return {
                "log_groups": log_groups,
                "error_logs": error_logs[:20]  # Limit to most recent 20 errors
            }
            
        except Exception as e:
            return {"error": str(e)}
    
    def _analyze_issues(self, stack_data: Dict, cloudtrail_data: Dict, logs_data: Dict) -> Dict[str, Any]:
        """Analyze gathered data to categorize and prioritize issues."""
        
        issues = []
        error_patterns = []
        severity = "LOW"
        
        # Analyze stack status
        stack_status = stack_data.get("stack_status", "UNKNOWN")
        if "FAILED" in stack_status or "ROLLBACK" in stack_status:
            severity = "HIGH"
            issues.append(f"Stack is in failed state: {stack_status}")
        
        # Analyze failed events
        failed_events = stack_data.get("failed_events", [])
        if failed_events:
            severity = "HIGH"
            for event in failed_events[:5]:  # Top 5 failures
                resource_id = event.get("LogicalResourceId", "Unknown")
                reason = event.get("ResourceStatusReason", "No reason provided")
                issues.append(f"Resource {resource_id} failed: {reason}")
                
                # Categorize error patterns
                if "permission" in reason.lower() or "access" in reason.lower():
                    error_patterns.append("PERMISSIONS")
                elif "limit" in reason.lower() or "quota" in reason.lower():
                    error_patterns.append("LIMITS")
                elif "validation" in reason.lower() or "invalid" in reason.lower():
                    error_patterns.append("VALIDATION")
                elif "already exists" in reason.lower():
                    error_patterns.append("CONFLICTS")
        
        # Analyze CloudTrail errors
        cloudtrail_errors = cloudtrail_data.get("error_events", [])
        if cloudtrail_errors:
            for error in cloudtrail_errors[:3]:
                error_code = error.get("ErrorCode", "Unknown")
                issues.append(f"API Error: {error_code}")
        
        # Analyze log errors
        log_errors = logs_data.get("error_logs", [])
        if log_errors:
            for log_error in log_errors[:3]:
                message = log_error.get("message", "")[:100]  # First 100 chars
                issues.append(f"Log Error: {message}")
        
        return {
            "severity": severity,
            "issues": issues,
            "error_patterns": list(set(error_patterns)),
            "failed_resources_count": len(stack_data.get("failed_resources", [])),
            "total_events": len(stack_data.get("events", [])),
            "stack_status": stack_status
        }
    
    def _create_expert_troubleshooting_prompt(
        self,
        stack_name: str,
        region: Optional[str],
        stack_data: Dict,
        cloudtrail_data: Dict,
        logs_data: Dict,
        issue_analysis: Dict,
        symptoms_description: Optional[str]
    ) -> str:
        """Create a comprehensive expert troubleshooting prompt for Claude."""
        
        stack_status = issue_analysis.get("stack_status", "UNKNOWN")
        severity = issue_analysis.get("severity", "LOW")
        issues = issue_analysis.get("issues", [])
        error_patterns = issue_analysis.get("error_patterns", [])
        
        prompt = f"""
You are an expert AWS CloudFormation troubleshooter with deep expertise in diagnosing and fixing complex infrastructure issues.

TROUBLESHOOTING REQUEST:
- Stack Name: {stack_name}
- Region: {region or 'us-east-1'}
- Current Status: {stack_status}
- Severity: {severity}
- User Symptoms: {symptoms_description or 'Stack deployment/update issues'}

DIAGNOSTIC DATA ANALYSIS:

Stack Information:
- Total Events: {issue_analysis.get('total_events', 0)}
- Failed Resources: {issue_analysis.get('failed_resources_count', 0)}
- CloudTrail Events: {len(cloudtrail_data.get('events', []))}
- Log Errors Found: {len(logs_data.get('error_logs', []))}

Identified Issues:
"""
        
        for i, issue in enumerate(issues[:10], 1):
            prompt += f"{i}. {issue}\n"
        
        if error_patterns:
            prompt += f"\nError Pattern Categories: {', '.join(error_patterns)}\n"
        
        prompt += f"""

SYSTEMATIC TROUBLESHOOTING APPROACH:

1. **IMMEDIATE ASSESSMENT**
   - Stack Status: {stack_status}
   - Critical Issues: {len([i for i in issues if any(word in i.lower() for word in ['failed', 'error', 'permission'])])}
   - Requires Immediate Action: {'YES' if severity == 'HIGH' else 'NO'}

2. **ROOT CAUSE ANALYSIS**
   Based on the diagnostic data, please analyze:
   
   **Failed Resources Analysis:**
   - Review each failed resource and its specific error message
   - Identify dependency chains and cascading failures
   - Determine if failures are related or independent
   
   **Permission Issues:** {'DETECTED' if 'PERMISSIONS' in error_patterns else 'NOT DETECTED'}
   - Check IAM roles and policies for CloudFormation
   - Verify service-linked roles exist
   - Validate cross-service permissions
   
   **Resource Limits:** {'DETECTED' if 'LIMITS' in error_patterns else 'NOT DETECTED'}
   - Check service quotas and account limits
   - Verify regional resource availability
   - Identify capacity constraints
   
   **Validation Errors:** {'DETECTED' if 'VALIDATION' in error_patterns else 'NOT DETECTED'}
   - Template syntax and structure issues
   - Resource property validation failures
   - Circular dependency detection

3. **DETAILED INVESTIGATION COMMANDS**
   
   Execute these commands for comprehensive analysis:
   
   ```bash
   # Get detailed stack information
   aws cloudformation describe-stacks --stack-name {stack_name} --region {region or 'us-east-1'}
   
   # Get all stack events with details
   aws cloudformation describe-stack-events --stack-name {stack_name} --region {region or 'us-east-1'}
   
   # Get current template
   aws cloudformation get-template --stack-name {stack_name} --region {region or 'us-east-1'}
   
   # Check stack resources status
   aws cloudformation describe-stack-resources --stack-name {stack_name} --region {region or 'us-east-1'}
   
   # Look for drift detection
   aws cloudformation detect-stack-drift --stack-name {stack_name} --region {region or 'us-east-1'}
   ```

4. **SPECIFIC FIXES BASED ON ERROR PATTERNS**
"""

        # Add specific guidance based on detected error patterns
        if 'PERMISSIONS' in error_patterns:
            prompt += """
   **Permission Fixes:**
   - Add missing IAM capabilities to CloudFormation deployment
   - Update IAM roles with required permissions
   - Check service-linked role requirements
   - Verify cross-account access if applicable
   
   ```bash
   # Check IAM role permissions
   aws iam get-role --role-name CloudFormationExecutionRole
   aws iam list-attached-role-policies --role-name CloudFormationExecutionRole
   ```
"""

        if 'LIMITS' in error_patterns:
            prompt += """
   **Resource Limit Fixes:**
   - Request service quota increases
   - Choose different resource types or sizes
   - Distribute resources across regions/AZs
   - Clean up unused resources
   
   ```bash
   # Check service quotas
   aws service-quotas get-service-quota --service-code ec2 --quota-code L-1216C47A
   aws service-quotas list-service-quotas --service-code cloudformation
   ```
"""

        if 'VALIDATION' in error_patterns:
            prompt += """
   **Template Validation Fixes:**
   - Fix template syntax errors
   - Add missing required properties
   - Resolve circular dependencies
   - Update resource configurations
   
   ```bash
   # Validate template syntax
   aws cloudformation validate-template --template-body file://template.yaml
   
   # Use linting tools
   cfn-lint template.yaml
   ```
"""

        prompt += f"""

5. **RESOLUTION STRATEGY**
   
   Based on the analysis, provide:
   - **Immediate Actions**: Critical fixes needed right now
   - **Template Corrections**: Specific changes to CloudFormation template
   - **Deployment Strategy**: How to safely apply fixes
   - **Verification Steps**: How to confirm fixes work
   - **Prevention Measures**: How to avoid similar issues

6. **MONITORING AND VERIFICATION**
   
   After implementing fixes:
   ```bash
   # Monitor deployment progress
   aws cloudformation wait stack-update-complete --stack-name {stack_name}
   
   # Verify all resources are healthy
   aws cloudformation describe-stack-resources --stack-name {stack_name}
   
   # Check for any drift
   aws cloudformation describe-stack-drift-detection-status --stack-name {stack_name}
   ```

Please provide a comprehensive analysis with specific, actionable solutions for each identified issue. Include exact CLI commands, template fixes, and step-by-step resolution procedures.
"""

        return prompt
    
    def _create_troubleshooting_workflow(self, stack_name: str, issue_analysis: Dict) -> List[str]:
        """Create a systematic troubleshooting workflow."""
        
        workflow = [
            "Assess current stack status and severity",
            "Gather comprehensive diagnostic data",
            "Analyze failed resources and error patterns",
            "Investigate root causes using CloudTrail and logs",
            "Categorize issues (permissions, limits, validation, conflicts)",
            "Apply targeted fixes based on error categories",
            "Validate fixes and redeploy",
            "Monitor deployment and verify success",
            "Set up preventive measures and monitoring"
        ]
        
        # Customize workflow based on detected issues
        if issue_analysis.get("severity") == "HIGH":
            workflow.insert(1, "🚨 URGENT: Address critical failures immediately")
        
        if "PERMISSIONS" in issue_analysis.get("error_patterns", []):
            workflow.insert(-2, "Update IAM roles and policies")
        
        if "LIMITS" in issue_analysis.get("error_patterns", []):
            workflow.insert(-2, "Request service quota increases or optimize resources")
        
        return workflow
    
    def _generate_cli_commands(self, stack_name: str, region: Optional[str], issue_analysis: Dict) -> List[str]:
        """Generate specific CLI commands for troubleshooting."""
        
        region_param = f"--region {region}" if region else ""
        
        commands = [
            f"aws cloudformation describe-stacks --stack-name {stack_name} {region_param}",
            f"aws cloudformation describe-stack-events --stack-name {stack_name} {region_param}",
            f"aws cloudformation describe-stack-resources --stack-name {stack_name} {region_param}",
            f"aws cloudformation get-template --stack-name {stack_name} {region_param}",
            f"aws cloudformation detect-stack-drift --stack-name {stack_name} {region_param}"
        ]
        
        # Add specific commands based on error patterns
        if "PERMISSIONS" in issue_analysis.get("error_patterns", []):
            commands.extend([
                "aws sts get-caller-identity",
                "aws iam list-attached-role-policies --role-name CloudFormationExecutionRole"
            ])
        
        if "LIMITS" in issue_analysis.get("error_patterns", []):
            commands.extend([
                "aws service-quotas list-service-quotas --service-code cloudformation",
                "aws ec2 describe-account-attributes"
            ])
        
        return commands
    
    def _generate_next_steps(self, issue_analysis: Dict) -> List[str]:
        """Generate specific next steps based on the analysis."""
        
        next_steps = []
        
        if issue_analysis.get("severity") == "HIGH":
            next_steps.append("🚨 IMMEDIATE: Stop any ongoing deployments to prevent further damage")
        
        error_patterns = issue_analysis.get("error_patterns", [])
        
        if "PERMISSIONS" in error_patterns:
            next_steps.extend([
                "Review and update IAM roles and policies",
                "Add required CloudFormation capabilities",
                "Verify service-linked roles exist"
            ])
        
        if "LIMITS" in error_patterns:
            next_steps.extend([
                "Check service quotas and request increases",
                "Consider alternative resource configurations",
                "Clean up unused resources to free capacity"
            ])
        
        if "VALIDATION" in error_patterns:
            next_steps.extend([
                "Fix template syntax and validation errors",
                "Add missing required resource properties",
                "Resolve circular dependencies"
            ])
        
        if "CONFLICTS" in error_patterns:
            next_steps.extend([
                "Resolve resource naming conflicts",
                "Check for existing resources with same names",
                "Update template with unique resource names"
            ])
        
        # Always add these general steps
        next_steps.extend([
            "Test fixes in development environment first",
            "Use change sets for production deployments",
            "Set up monitoring and alerting for future issues"
        ])
        
        return next_steps
    
    def _create_fallback_prompt(self, stack_name: str, region: Optional[str], symptoms: Optional[str], error: str) -> Dict[str, Any]:
        """Create a fallback prompt when data gathering fails."""
        
        expert_prompt = f"""
You are an expert AWS CloudFormation troubleshooter. Help diagnose and fix issues with this stack:

STACK INFORMATION:
- Stack Name: {stack_name}
- Region: {region or 'us-east-1'}
- Symptoms: {symptoms or 'Stack deployment or update issues'}
- Note: Enhanced diagnostic data unavailable due to: {error}

SYSTEMATIC TROUBLESHOOTING APPROACH:

1. **GATHER INFORMATION**
   ```bash
   # Check stack status
   aws cloudformation describe-stacks --stack-name {stack_name}
   
   # Get stack events
   aws cloudformation describe-stack-events --stack-name {stack_name}
   
   # List stack resources
   aws cloudformation describe-stack-resources --stack-name {stack_name}
   
   # Get template
   aws cloudformation get-template --stack-name {stack_name}
   ```

2. **ANALYZE FAILURES**
   - Identify failed resources from stack events
   - Check resource status reasons for error details
   - Look for patterns in error messages
   - Categorize issues: permissions, limits, validation, conflicts

3. **INVESTIGATE ROOT CAUSES**
   - Review CloudTrail logs for API call failures
   - Check CloudWatch logs for application errors
   - Validate template syntax and properties
   - Verify IAM permissions and service limits

4. **PROVIDE SOLUTIONS**
   - Specific fixes for identified issues
   - Template corrections if needed
   - CLI commands to resolve problems
   - Best practices to prevent recurrence

5. **VERIFICATION**
   - Commands to verify fixes
   - Monitoring recommendations
   - Rollback procedures if needed

Please provide a comprehensive analysis and step-by-step resolution plan.
"""

        return {
            "expert_prompt_for_claude": expert_prompt,
            "troubleshooting_workflow": [
                "Gather stack information and events",
                "Analyze failure patterns and error messages",
                "Investigate root causes",
                "Provide specific fixes",
                "Verify solutions"
            ],
            "cli_commands": [
                f"aws cloudformation describe-stacks --stack-name {stack_name}",
                f"aws cloudformation describe-stack-events --stack-name {stack_name}",
                f"aws cloudformation describe-stack-resources --stack-name {stack_name}"
            ],
            "error": error
        }

    def enhance_troubleshooting_request(
        self,
        stack_name: str,
        region: Optional[str] = None,
        include_logs: bool = True,
        include_cloudtrail: bool = True,
        time_window_hours: int = 24,
        symptoms_description: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Main method to enhance troubleshooting requests into expert prompts.
        
        This is the primary interface that transforms basic troubleshooting requests
        into comprehensive expert-level prompts with real AWS diagnostic data.
        """
        return self.create_enhanced_troubleshooting_prompt(
            stack_name=stack_name,
            region=region,
            include_logs=include_logs,
            include_cloudtrail=include_cloudtrail,
            max_events=50,
            time_window_hours=time_window_hours,
            symptoms_description=symptoms_description
        )
