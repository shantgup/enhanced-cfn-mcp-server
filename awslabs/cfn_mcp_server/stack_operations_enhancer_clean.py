#!/usr/bin/env python3
"""
Clean Stack Operations Prompt Enhancement Module

This module transforms basic stack operation requests into expert-level prompts for Claude.
It provides comprehensive CloudFormation stack analysis, monitoring, and operational guidance.
"""

import json
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from awslabs.cfn_mcp_server.aws_client import get_aws_client


class StackOperationsEnhancer:
    """
    Clean stack operations prompt enhancer that transforms basic stack operation requests
    into comprehensive expert-level prompts for Claude.
    """
    
    def __init__(self):
        self.operation_patterns = {
            'deployment': ['deploy', 'create', 'update', 'rollback'],
            'monitoring': ['status', 'health', 'events', 'logs'],
            'troubleshooting': ['failed', 'error', 'issue', 'problem'],
            'optimization': ['performance', 'cost', 'efficiency', 'scaling'],
            'security': ['security', 'compliance', 'audit', 'permissions']
        }
        
        self.stack_states = {
            'CREATE_IN_PROGRESS': {'severity': 'INFO', 'action': 'Monitor deployment progress'},
            'CREATE_COMPLETE': {'severity': 'SUCCESS', 'action': 'Verify resources and test functionality'},
            'CREATE_FAILED': {'severity': 'ERROR', 'action': 'Analyze failure and implement fixes'},
            'UPDATE_IN_PROGRESS': {'severity': 'INFO', 'action': 'Monitor update progress'},
            'UPDATE_COMPLETE': {'severity': 'SUCCESS', 'action': 'Validate changes and test'},
            'UPDATE_FAILED': {'severity': 'ERROR', 'action': 'Rollback and analyze issues'},
            'DELETE_IN_PROGRESS': {'severity': 'WARNING', 'action': 'Monitor deletion progress'},
            'DELETE_COMPLETE': {'severity': 'SUCCESS', 'action': 'Confirm resource cleanup'},
            'DELETE_FAILED': {'severity': 'ERROR', 'action': 'Manual cleanup may be required'},
            'ROLLBACK_IN_PROGRESS': {'severity': 'WARNING', 'action': 'Monitor rollback progress'},
            'ROLLBACK_COMPLETE': {'severity': 'WARNING', 'action': 'Investigate original failure'},
            'ROLLBACK_FAILED': {'severity': 'CRITICAL', 'action': 'Immediate intervention required'}
        }

    async def generate_stack_status_prompt(
        self,
        stack_name: str,
        region: Optional[str] = None,
        include_resources: bool = True,
        include_events: bool = True,
        analysis_focus: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Generate comprehensive expert-level stack status analysis prompt for Claude.
        
        Args:
            stack_name: Name of the CloudFormation stack
            region: AWS region
            include_resources: Whether to include resource details
            include_events: Whether to include stack events
            analysis_focus: Specific focus area (deployment, monitoring, troubleshooting, etc.)
            
        Returns:
            Dictionary containing expert prompt and stack analysis context
        """
        try:
            # Get stack information
            stack_info = await self._get_stack_information(stack_name, region, include_resources, include_events)
            
            # Analyze stack health and status
            health_analysis = self._analyze_stack_health(stack_info)
            
            # Detect operational patterns
            operation_type = self._detect_operation_type(stack_info, analysis_focus)
            
            # Generate expert prompt
            expert_prompt = self._build_stack_analysis_prompt(
                stack_name=stack_name,
                stack_info=stack_info,
                health_analysis=health_analysis,
                operation_type=operation_type,
                region=region,
                analysis_focus=analysis_focus
            )
            
            return {
                'expert_prompt_for_claude': expert_prompt,
                'stack_information': stack_info,
                'health_analysis': health_analysis,
                'operation_type': operation_type,
                'monitoring_workflow': self._generate_monitoring_workflow(operation_type),
                'investigation_commands': self._generate_stack_investigation_commands(stack_name, region),
                'operational_checklist': self._generate_operational_checklist(health_analysis, operation_type),
                'alerting_recommendations': self._generate_alerting_recommendations(stack_info),
                'next_actions': self._generate_next_actions(health_analysis, operation_type),
                'region': region or 'us-east-1',
                'timestamp': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f"Stack analysis failed: {str(e)}",
                'expert_prompt_for_claude': self._generate_error_analysis_prompt(str(e), stack_name, region)
            }

    async def generate_stack_drift_prompt(
        self,
        stack_name: str,
        region: Optional[str] = None
    ) -> Dict[str, Any]:
        """Generate expert-level stack drift analysis prompt."""
        try:
            # Initiate drift detection
            drift_info = await self._detect_stack_drift(stack_name, region)
            
            expert_prompt = self._build_drift_analysis_prompt(stack_name, drift_info, region)
            
            return {
                'expert_prompt_for_claude': expert_prompt,
                'drift_analysis': drift_info,
                'remediation_workflow': self._generate_drift_remediation_workflow(),
                'investigation_commands': self._generate_drift_investigation_commands(stack_name, region),
                'prevention_measures': self._generate_drift_prevention_measures(),
                'region': region or 'us-east-1',
                'timestamp': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f"Drift analysis failed: {str(e)}",
                'expert_prompt_for_claude': self._generate_drift_error_prompt(str(e), stack_name, region)
            }

    async def _get_stack_information(
        self,
        stack_name: str,
        region: Optional[str],
        include_resources: bool,
        include_events: bool
    ) -> Dict[str, Any]:
        """Get comprehensive stack information."""
        try:
            cfn_client = get_aws_client('cloudformation', region)
            
            # Get stack details
            stack_response = cfn_client.describe_stacks(StackName=stack_name)
            stack = stack_response['Stacks'][0] if stack_response['Stacks'] else None
            
            result = {
                'stack_details': stack,
                'resources': [],
                'events': [],
                'template': None,
                'success': True
            }
            
            if not stack:
                result['success'] = False
                result['error'] = f"Stack {stack_name} not found"
                return result
            
            # Get resources if requested
            if include_resources:
                try:
                    resources_response = cfn_client.describe_stack_resources(StackName=stack_name)
                    result['resources'] = resources_response.get('StackResources', [])
                except Exception as e:
                    result['resources_error'] = str(e)
            
            # Get events if requested
            if include_events:
                try:
                    events_response = cfn_client.describe_stack_events(StackName=stack_name)
                    result['events'] = events_response.get('StackEvents', [])[:50]  # Last 50 events
                except Exception as e:
                    result['events_error'] = str(e)
            
            # Get template
            try:
                template_response = cfn_client.get_template(StackName=stack_name)
                result['template'] = template_response.get('TemplateBody')
            except Exception as e:
                result['template_error'] = str(e)
            
            return result
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'stack_name': stack_name
            }

    def _analyze_stack_health(self, stack_info: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze stack health and identify issues."""
        if not stack_info.get('success'):
            return {
                'overall_health': 'UNKNOWN',
                'severity': 'ERROR',
                'issues': [{'type': 'stack_not_found', 'description': stack_info.get('error', 'Unknown error')}],
                'recommendations': ['Verify stack name and region', 'Check AWS credentials and permissions']
            }
        
        stack = stack_info.get('stack_details', {})
        resources = stack_info.get('resources', [])
        events = stack_info.get('events', [])
        
        # Analyze stack status
        stack_status = stack.get('StackStatus', 'UNKNOWN')
        stack_state_info = self.stack_states.get(stack_status, {'severity': 'UNKNOWN', 'action': 'Investigate status'})
        
        # Analyze resource health
        failed_resources = [r for r in resources if r.get('ResourceStatus', '').endswith('_FAILED')]
        in_progress_resources = [r for r in resources if r.get('ResourceStatus', '').endswith('_IN_PROGRESS')]
        
        # Analyze recent events
        recent_errors = []
        for event in events[:10]:  # Check last 10 events
            if event.get('ResourceStatus', '').endswith('_FAILED'):
                recent_errors.append({
                    'resource': event.get('LogicalResourceId'),
                    'status': event.get('ResourceStatus'),
                    'reason': event.get('ResourceStatusReason', 'No reason provided'),
                    'timestamp': event.get('Timestamp')
                })
        
        # Determine overall health
        if stack_status.endswith('_FAILED'):
            overall_health = 'CRITICAL'
        elif failed_resources or recent_errors:
            overall_health = 'DEGRADED'
        elif stack_status.endswith('_IN_PROGRESS'):
            overall_health = 'TRANSITIONING'
        elif stack_status.endswith('_COMPLETE'):
            overall_health = 'HEALTHY'
        else:
            overall_health = 'UNKNOWN'
        
        return {
            'overall_health': overall_health,
            'stack_status': stack_status,
            'severity': stack_state_info['severity'],
            'recommended_action': stack_state_info['action'],
            'total_resources': len(resources),
            'failed_resources': len(failed_resources),
            'in_progress_resources': len(in_progress_resources),
            'recent_errors': recent_errors,
            'stack_age_days': self._calculate_stack_age(stack.get('CreationTime')),
            'last_updated': stack.get('LastUpdatedTime'),
            'drift_status': stack.get('DriftInformation', {}).get('StackDriftStatus', 'NOT_CHECKED')
        }

    def _detect_operation_type(self, stack_info: Dict[str, Any], analysis_focus: Optional[str]) -> str:
        """Detect the type of operation being performed."""
        if analysis_focus:
            return analysis_focus
        
        if not stack_info.get('success'):
            return 'troubleshooting'
        
        stack_status = stack_info.get('stack_details', {}).get('StackStatus', '')
        
        if stack_status.endswith('_IN_PROGRESS'):
            return 'deployment'
        elif stack_status.endswith('_FAILED'):
            return 'troubleshooting'
        elif stack_status.endswith('_COMPLETE'):
            return 'monitoring'
        else:
            return 'general'

    def _build_stack_analysis_prompt(
        self,
        stack_name: str,
        stack_info: Dict[str, Any],
        health_analysis: Dict[str, Any],
        operation_type: str,
        region: Optional[str],
        analysis_focus: Optional[str]
    ) -> str:
        """Build comprehensive expert stack analysis prompt for Claude."""
        
        focus_guidance = {
            'deployment': 'Focus on deployment progress, resource creation status, and deployment best practices.',
            'monitoring': 'Focus on operational health, performance metrics, and proactive monitoring strategies.',
            'troubleshooting': 'Focus on error analysis, root cause identification, and systematic problem resolution.',
            'optimization': 'Focus on performance improvements, cost optimization, and operational efficiency.',
            'security': 'Focus on security posture, compliance validation, and access control review.'
        }
        
        prompt = f"""
You are an expert AWS CloudFormation operations specialist with deep expertise in stack management, monitoring, and troubleshooting.

STACK ANALYSIS REQUEST:
- Stack Name: {stack_name}
- Region: {region or 'us-east-1'}
- Operation Type: {operation_type}
- Overall Health: {health_analysis['overall_health']}
- Stack Status: {health_analysis.get('stack_status', 'UNKNOWN')}
- Analysis Focus: {analysis_focus or 'comprehensive'}

{focus_guidance.get(operation_type, 'Provide comprehensive operational analysis covering deployment, monitoring, and optimization.')}

CURRENT STACK STATUS:
"""
        
        if stack_info.get('success'):
            stack = stack_info['stack_details']
            prompt += f"""
- Status: {health_analysis.get('stack_status', 'UNKNOWN')} ({health_analysis['severity']})
- Total Resources: {health_analysis['total_resources']}
- Failed Resources: {health_analysis['failed_resources']}
- In Progress: {health_analysis['in_progress_resources']}
- Stack Age: {health_analysis['stack_age_days']} days
- Drift Status: {health_analysis['drift_status']}
- Recommended Action: {health_analysis['recommended_action']}
"""
            
            if health_analysis['recent_errors']:
                prompt += f"\n⚠️ Recent Errors Detected ({len(health_analysis['recent_errors'])}):\n"
                for error in health_analysis['recent_errors'][:3]:
                    prompt += f"- {error['resource']}: {error['status']} - {error['reason']}\n"
        else:
            prompt += f"❌ Stack Access Error: {stack_info.get('error', 'Unknown error')}\n"
        
        prompt += f"""

EXPERT ANALYSIS REQUIREMENTS:

1. **OPERATIONAL STATUS ASSESSMENT**
   - Evaluate current stack health and stability
   - Identify immediate risks and required actions
   - Assess resource status and dependencies
   - Review recent operational events and patterns

2. **DEPLOYMENT ANALYSIS** (if applicable)
   - Monitor deployment progress and timeline
   - Identify potential deployment bottlenecks
   - Validate resource creation sequence
   - Assess rollback readiness and procedures

3. **ERROR AND FAILURE ANALYSIS** (if applicable)
   - Analyze failed resources and error patterns
   - Identify root causes and contributing factors
   - Evaluate cascading failure impacts
   - Develop systematic resolution strategies

4. **PERFORMANCE AND EFFICIENCY REVIEW**
   - Assess resource utilization and performance
   - Identify optimization opportunities
   - Review cost implications and efficiency
   - Evaluate scaling and capacity planning

5. **OPERATIONAL EXCELLENCE EVALUATION**
   - Review monitoring and alerting configuration
   - Assess backup and disaster recovery readiness
   - Evaluate maintenance and update procedures
   - Check compliance with operational best practices

6. **SECURITY AND COMPLIANCE POSTURE**
   - Review access controls and permissions
   - Validate security configurations
   - Check compliance with security standards
   - Assess audit trail and logging completeness

DELIVERABLES REQUIRED:

1. **Executive Summary**: Current status and critical findings
2. **Detailed Health Assessment**: Resource-by-resource analysis
3. **Operational Recommendations**: Specific improvement actions
4. **Monitoring Strategy**: Comprehensive observability plan
5. **Incident Response Plan**: Procedures for common issues
6. **Maintenance Schedule**: Ongoing operational tasks
7. **Performance Optimization**: Efficiency improvements

INVESTIGATION COMMANDS:
Provide specific AWS CLI commands for deeper analysis:
- Stack event analysis commands
- Resource status validation commands
- Performance monitoring commands
- Security audit commands
- Cost analysis commands

Please provide expert-level operational guidance with specific, actionable recommendations for maintaining and optimizing this CloudFormation stack.

Focus on production-ready solutions that ensure reliability, security, and operational excellence.
"""
        
        return prompt

    def _build_drift_analysis_prompt(self, stack_name: str, drift_info: Dict[str, Any], region: Optional[str]) -> str:
        """Build expert drift analysis prompt."""
        return f"""
You are an expert AWS CloudFormation drift detection specialist with deep expertise in infrastructure consistency and change management.

DRIFT DETECTION REQUEST:
- Stack Name: {stack_name}
- Region: {region or 'us-east-1'}
- Drift Status: {drift_info.get('drift_status', 'UNKNOWN')}

DRIFT ANALYSIS REQUIREMENTS:

1. **DRIFT ASSESSMENT**
   - Analyze detected configuration drift
   - Identify resources with out-of-band changes
   - Evaluate impact of drift on stack integrity
   - Assess security and compliance implications

2. **ROOT CAUSE ANALYSIS**
   - Identify sources of configuration drift
   - Review change management processes
   - Analyze access patterns and permissions
   - Evaluate automation and manual changes

3. **REMEDIATION STRATEGY**
   - Develop drift correction procedures
   - Plan template updates vs. resource corrections
   - Design change management improvements
   - Implement drift prevention measures

4. **OPERATIONAL IMPROVEMENTS**
   - Enhance monitoring and alerting
   - Strengthen access controls
   - Improve change management processes
   - Implement automated drift detection

Please provide comprehensive drift analysis with specific remediation steps and prevention strategies.
"""

    def _generate_monitoring_workflow(self, operation_type: str) -> List[str]:
        """Generate monitoring workflow based on operation type."""
        base_workflow = [
            "Monitor stack status and events continuously",
            "Track resource health and performance metrics",
            "Review CloudWatch logs and alarms",
            "Validate security and compliance posture",
            "Assess cost and resource utilization",
            "Check for configuration drift",
            "Update monitoring and alerting as needed"
        ]
        
        operation_workflows = {
            'deployment': [
                "Monitor deployment progress in real-time",
                "Track resource creation sequence and dependencies",
                "Watch for deployment failures and rollback triggers",
                "Validate post-deployment functionality",
                "Update monitoring baselines for new resources"
            ],
            'troubleshooting': [
                "Analyze stack events and error patterns",
                "Investigate failed resource configurations",
                "Review CloudTrail logs for change history",
                "Validate permissions and access controls",
                "Test remediation steps in non-production"
            ]
        }
        
        return operation_workflows.get(operation_type, base_workflow)

    def _generate_stack_investigation_commands(self, stack_name: str, region: Optional[str]) -> List[str]:
        """Generate AWS CLI commands for stack investigation."""
        region_param = f"--region {region}" if region else ""
        
        return [
            f"aws cloudformation describe-stacks --stack-name {stack_name} {region_param}",
            f"aws cloudformation describe-stack-events --stack-name {stack_name} {region_param}",
            f"aws cloudformation describe-stack-resources --stack-name {stack_name} {region_param}",
            f"aws cloudformation get-template --stack-name {stack_name} {region_param}",
            f"aws cloudformation detect-stack-drift --stack-name {stack_name} {region_param}",
            f"aws cloudformation describe-stack-drift-detection-status --stack-name {stack_name} {region_param}",
            f"aws cloudformation list-stack-resources --stack-name {stack_name} {region_param}",
            f"aws logs describe-log-groups --log-group-name-prefix /aws/cloudformation/{stack_name} {region_param}",
            f"aws cloudtrail lookup-events --lookup-attributes AttributeKey=ResourceName,AttributeValue={stack_name} {region_param}"
        ]

    def _generate_operational_checklist(self, health_analysis: Dict[str, Any], operation_type: str) -> List[str]:
        """Generate operational checklist based on analysis."""
        checklist = [
            "✓ Stack status is healthy and stable",
            "✓ All resources are in expected state",
            "✓ No recent deployment failures",
            "✓ CloudWatch monitoring is active",
            "✓ Security configurations are valid",
            "✓ Backup procedures are in place",
            "✓ Cost optimization is implemented",
            "✓ Documentation is up to date"
        ]
        
        if health_analysis['overall_health'] == 'CRITICAL':
            checklist = [
                "❌ Critical issues require immediate attention",
                "❌ Failed resources need investigation",
                "❌ Error patterns require analysis",
                "❌ Rollback procedures may be needed"
            ]
        elif health_analysis['overall_health'] == 'DEGRADED':
            checklist.extend([
                "⚠️ Some resources have issues",
                "⚠️ Recent errors need investigation",
                "⚠️ Performance may be impacted"
            ])
        
        return checklist

    def _generate_alerting_recommendations(self, stack_info: Dict[str, Any]) -> List[str]:
        """Generate alerting recommendations."""
        return [
            "Set up CloudWatch alarms for stack status changes",
            "Configure SNS notifications for deployment events",
            "Monitor resource health and performance metrics",
            "Alert on configuration drift detection",
            "Track cost anomalies and budget thresholds",
            "Monitor security group and IAM changes",
            "Set up log-based alerts for error patterns",
            "Configure automated response for common issues"
        ]

    def _generate_next_actions(self, health_analysis: Dict[str, Any], operation_type: str) -> List[str]:
        """Generate next actions based on analysis."""
        if health_analysis['overall_health'] == 'CRITICAL':
            return [
                "Immediately investigate failed resources",
                "Prepare rollback procedures if needed",
                "Analyze error patterns and root causes",
                "Implement emergency fixes",
                "Update incident response procedures"
            ]
        elif health_analysis['overall_health'] == 'DEGRADED':
            return [
                "Investigate resource issues",
                "Plan remediation steps",
                "Test fixes in non-production",
                "Update monitoring and alerting",
                "Review change management processes"
            ]
        else:
            return [
                "Continue monitoring stack health",
                "Review performance metrics",
                "Plan optimization improvements",
                "Update documentation",
                "Schedule maintenance activities"
            ]

    async def _detect_stack_drift(self, stack_name: str, region: Optional[str]) -> Dict[str, Any]:
        """Detect stack drift."""
        try:
            cfn_client = get_aws_client('cloudformation', region)
            
            # Start drift detection
            response = cfn_client.detect_stack_drift(StackName=stack_name)
            drift_detection_id = response['StackDriftDetectionId']
            
            return {
                'drift_detection_id': drift_detection_id,
                'drift_status': 'DETECTION_IN_PROGRESS',
                'success': True
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'drift_status': 'DETECTION_FAILED'
            }

    def _generate_drift_remediation_workflow(self) -> List[str]:
        """Generate drift remediation workflow."""
        return [
            "Identify all resources with configuration drift",
            "Analyze the nature and impact of each drift",
            "Determine if drift should be corrected or accepted",
            "Update CloudFormation template to match desired state",
            "Plan remediation deployment strategy",
            "Test remediation in non-production environment",
            "Execute remediation with proper change management",
            "Validate post-remediation stack consistency",
            "Implement drift prevention measures"
        ]

    def _generate_drift_investigation_commands(self, stack_name: str, region: Optional[str]) -> List[str]:
        """Generate drift investigation commands."""
        region_param = f"--region {region}" if region else ""
        
        return [
            f"aws cloudformation detect-stack-drift --stack-name {stack_name} {region_param}",
            f"aws cloudformation describe-stack-drift-detection-status --stack-name {stack_name} {region_param}",
            f"aws cloudformation describe-stack-resource-drifts --stack-name {stack_name} {region_param}",
            f"aws config get-compliance-details-by-config-rule --config-rule-name <rule-name> {region_param}",
            f"aws cloudtrail lookup-events --lookup-attributes AttributeKey=ResourceName,AttributeValue={stack_name} {region_param}"
        ]

    def _generate_drift_prevention_measures(self) -> List[str]:
        """Generate drift prevention measures."""
        return [
            "Implement strict change management processes",
            "Use AWS Config rules for compliance monitoring",
            "Set up automated drift detection schedules",
            "Restrict direct resource modification permissions",
            "Implement infrastructure as code governance",
            "Use AWS CloudTrail for change auditing",
            "Set up alerts for out-of-band changes",
            "Regular drift detection and remediation cycles"
        ]

    def _calculate_stack_age(self, creation_time) -> int:
        """Calculate stack age in days."""
        if not creation_time:
            return 0
        
        try:
            if isinstance(creation_time, str):
                creation_time = datetime.fromisoformat(creation_time.replace('Z', '+00:00'))
            
            age = datetime.now(creation_time.tzinfo) - creation_time
            return age.days
        except:
            return 0

    def _generate_error_analysis_prompt(self, error: str, stack_name: str, region: Optional[str]) -> str:
        """Generate error analysis prompt."""
        return f"""
You are an expert AWS CloudFormation troubleshooter. An error occurred during stack analysis.

STACK ANALYSIS ERROR:
- Stack Name: {stack_name}
- Region: {region or 'us-east-1'}
- Error: {error}

Please analyze the error and provide:
1. Root cause analysis of the access or permission issue
2. Specific remediation steps to resolve the error
3. Alternative approaches for stack analysis
4. Prevention measures for similar issues

Focus on actionable solutions to restore stack visibility and management capabilities.
"""

    def _generate_drift_error_prompt(self, error: str, stack_name: str, region: Optional[str]) -> str:
        """Generate drift error analysis prompt."""
        return f"""
You are an expert AWS CloudFormation drift detection specialist. An error occurred during drift analysis.

DRIFT DETECTION ERROR:
- Stack Name: {stack_name}
- Region: {region or 'us-east-1'}
- Error: {error}

Please analyze the error and provide:
1. Root cause analysis of the drift detection failure
2. Alternative drift detection approaches
3. Manual drift identification procedures
4. Prevention measures for drift detection issues

Focus on actionable solutions to restore drift detection capabilities.
"""
