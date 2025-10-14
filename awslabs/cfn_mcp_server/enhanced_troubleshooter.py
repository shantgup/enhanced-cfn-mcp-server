"""
Enhanced CloudFormation Troubleshooter with Autonomous Fixing

This module extends the existing troubleshooter with deep template analysis,
automatic fixing capabilities, and autonomous deployment features.
"""

import json
from typing import Dict, List, Any, Optional
try:
    import yaml
except ImportError:
    yaml = None
from datetime import datetime, timedelta
import logging

from .troubleshooter import CloudFormationTroubleshooter
from .template_analyzer import TemplateAnalyzer
from .template_fixer import TemplateFixer
from .autonomous_deployer import AutonomousDeployer

logger = logging.getLogger(__name__)

class EnhancedCloudFormationTroubleshooter(CloudFormationTroubleshooter):
    """Enhanced troubleshooter with autonomous fixing capabilities"""
    
    def __init__(self, region: str = None, config=None):
        """Initialize the enhanced troubleshooter"""
        super().__init__(region, config)
        self.template_analyzer = TemplateAnalyzer()
        self.template_fixer = TemplateFixer()
        self.autonomous_deployer = AutonomousDeployer(region=self.region)
    
    async def comprehensive_analysis(
        self,
        stack_name: str,
        include_template_analysis: bool = True,
        symptoms_description: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Perform comprehensive analysis including template deep-dive
        
        Args:
            stack_name: CloudFormation stack name
            include_template_analysis: Whether to perform deep template analysis
            symptoms_description: Optional description of observed symptoms
            
        Returns:
            Comprehensive analysis results with actionable recommendations
        """
        try:
            # Start with base troubleshooting analysis (CloudFormation events only)
            base_analysis = await self.analyze_stack(
                stack_name=stack_name,
                include_logs=False,
                include_cloudtrail=False,
                time_window_hours=24,
                symptoms_description=symptoms_description
            )
            
            # Enhanced analysis structure
            enhanced_analysis = {
                'status': base_analysis.get('status', 'success'),
                'stack_name': stack_name,
                'analysis_timestamp': datetime.utcnow().isoformat(),
                'base_analysis': base_analysis,
                'template_analysis': {},
                'issue_correlation': {},
                'fix_recommendations': [],
                'autonomous_fix_plan': {},
                'deployment_readiness': {}
            }
            
            # Get stack template for analysis
            stack_template = base_analysis.get('raw_data', {}).get('stack_info', {}).get('stack_template')
            
            # Initialize template_analysis with default empty structure
            template_analysis = {
                'template_valid': False,
                'issues': [],
                'dependencies': [],
                'resource_analysis': {},
                'security_issues': [],
                'best_practice_violations': [],
                'recommendations': []
            }
            
            if stack_template and include_template_analysis:
                # Simple pass-through - let Q CLI handle template analysis
                template_analysis = {
                    'template_valid': True,
                    'raw_template': stack_template,
                    'message': 'Template provided for Q CLI analysis'
                }
            
            # Store template analysis results
            enhanced_analysis['template_analysis'] = template_analysis
            
            # Correlate template issues with stack events
            stack_events = base_analysis.get('raw_data', {}).get('stack_info', {}).get('stack_events', [])
            if stack_events and template_analysis.get('template_valid'):
                correlation = self.template_analyzer.correlate_with_stack_events(
                    template_analysis, 
                    stack_events
                )
                enhanced_analysis['issue_correlation'] = correlation
                
                # Generate fix recommendations
                fix_recommendations = self._generate_comprehensive_fix_recommendations(
                    template_analysis,
                    correlation if 'correlation' in locals() else {},
                    base_analysis
                )
                enhanced_analysis['fix_recommendations'] = fix_recommendations
                
                # Create autonomous fix plan
                autonomous_plan = self._create_autonomous_fix_plan(
                    stack_template,
                    template_analysis,
                    correlation if 'correlation' in locals() else {},
                    stack_name
                )
                enhanced_analysis['autonomous_fix_plan'] = autonomous_plan
                
                # Assess deployment readiness
                readiness_assessment = self._assess_deployment_readiness(
                    template_analysis,
                    base_analysis
                )
                enhanced_analysis['deployment_readiness'] = readiness_assessment
            
            # Create comprehensive summary
            enhanced_analysis['comprehensive_summary'] = self._create_comprehensive_summary(enhanced_analysis)
            
            # Add context system metadata
            enhanced_analysis['context_system'] = self._get_available_contexts()
            
            return enhanced_analysis
            
        except Exception as e:
            logger.exception(f"Error in comprehensive analysis: {e}")
            return {
                'status': 'error',
                'error': str(e),
                'stack_name': stack_name,
                'analysis_timestamp': datetime.utcnow().isoformat()
            }
    
    def _get_available_contexts(self) -> Dict[str, Any]:
        """Return metadata about available context files for Q CLI"""
        return {
            "description": "CloudFormation troubleshooting context files are available to help diagnose specific scenarios",
            "usage_instructions": "Analyze the stack events and failure patterns to determine which scenarios might apply, then call get_cloudformation_context(context_name) for detailed guidance",
            "available_contexts": [
                {
                    "name": "custom_resource_debugging",
                    "description": "For failures involving custom resources or Lambda-backed resources",
                    "triggers": [
                        "Custom resource failures", 
                        "ServiceToken present in failed resources", 
                        "Lambda timeout errors",
                        "Custom resource response format issues"
                    ]
                },
                {
                    "name": "nested_stack_troubleshooting",
                    "description": "For failures in nested CloudFormation stacks",
                    "triggers": [
                        "AWS::CloudFormation::Stack resource failures", 
                        "Nested stack CREATE_FAILED or UPDATE_FAILED",
                        "Cross-stack parameter issues",
                        "Parent-child stack dependency problems"
                    ]
                },
                {
                    "name": "drift_detection_guide",
                    "description": "For suspected out-of-band changes to stack resources",
                    "triggers": [
                        "UPDATE_FAILED with no template changes", 
                        "Resource already exists errors", 
                        "Unexpected resource states",
                        "Manual changes outside CloudFormation"
                    ]
                },
                {
                    "name": "permission_issues_guide",
                    "description": "For IAM and permission-related failures",
                    "triggers": [
                        "Access denied errors",
                        "Insufficient permissions",
                        "Cross-account role issues",
                        "Service-linked role problems"
                    ]
                },
                {
                    "name": "rollback_analysis_guide",
                    "description": "For understanding and recovering from rollback scenarios",
                    "triggers": [
                        "ROLLBACK_COMPLETE status",
                        "ROLLBACK_FAILED status", 
                        "UPDATE_ROLLBACK scenarios",
                        "Stack stuck in rollback"
                    ]
                }
            ]
        }
    

    
    async def fix_and_deploy(
        self,
        stack_name: str,
        auto_apply_fixes: bool = True,
        max_iterations: int = 5,
        parameters: Optional[List[Dict]] = None,
        capabilities: Optional[List[str]] = None,
        tags: Optional[List[Dict]] = None
    ) -> Dict[str, Any]:
        """
        Automatically fix template issues and deploy stack
        
        Args:
            stack_name: CloudFormation stack name
            auto_apply_fixes: Whether to automatically apply fixes
            max_iterations: Maximum fix-deploy iterations
            parameters: Stack parameters
            capabilities: IAM capabilities
            tags: Stack tags
            
        Returns:
            Deployment result with applied fixes and final status
        """
        try:
            result = {
                'success': False,
                'stack_name': stack_name,
                'timestamp': datetime.utcnow().isoformat(),
                'analysis_phase': {},
                'fixing_phase': {},
                'deployment_phase': {},
                'final_status': None
            }
            
            # Phase 1: Comprehensive Analysis
            logger.info(f"Phase 1: Analyzing stack {stack_name}")
            analysis = await self.comprehensive_analysis(stack_name)
            result['analysis_phase'] = {
                'status': 'completed',
                'issues_found': len(analysis.get('template_analysis', {}).get('issues', [])),
                'security_issues': len(analysis.get('template_analysis', {}).get('security_issues', [])),
                'missing_components': len(analysis.get('template_analysis', {}).get('missing_components', []))
            }
            
            # Get original template
            original_template = analysis.get('base_analysis', {}).get('raw_data', {}).get('stack_info', {}).get('stack_template')
            
            if not original_template:
                result['analysis_phase']['error'] = 'Could not retrieve stack template'
                return result
            
            # Phase 2: Template Fixing
            logger.info(f"Phase 2: Fixing template issues")
            template_analysis = analysis.get('template_analysis', {})
            
            if template_analysis.get('issues') or template_analysis.get('security_issues'):
                fix_result = self.template_fixer.fix_template(
                    original_template,
                    template_analysis,
                    auto_apply=auto_apply_fixes
                )
                
                result['fixing_phase'] = {
                    'status': 'completed',
                    'fixes_applied': len(fix_result.get('fixes_applied', [])),
                    'fixes_skipped': len(fix_result.get('fixes_skipped', [])),
                    'template_fixed': fix_result.get('success', False)
                }
                
                if fix_result.get('success'):
                    fixed_template = fix_result['fixed_template']
                else:
                    logger.warning("Template fixing failed, using original template")
                    fixed_template = original_template
                    result['fixing_phase']['error'] = 'Template fixing failed'
            else:
                logger.info("No template issues found, proceeding with original template")
                fixed_template = original_template
                result['fixing_phase'] = {
                    'status': 'skipped',
                    'reason': 'No issues found in template'
                }
            
            # Phase 3: Autonomous Deployment
            logger.info(f"Phase 3: Deploying stack with autonomous fixing")
            deployment_result = self.autonomous_deployer.deploy_with_auto_fix(
                stack_name=stack_name,
                template=fixed_template,
                parameters=parameters,
                capabilities=capabilities,
                tags=tags,
                max_iterations=max_iterations
            )
            
            result['deployment_phase'] = {
                'status': 'completed' if deployment_result.get('success') else 'failed',
                'deployment_attempts': len(deployment_result.get('deployment_attempts', [])),
                'total_fixes_applied': len(deployment_result.get('total_fixes_applied', [])),
                'final_stack_status': deployment_result.get('final_stack_status')
            }
            
            if deployment_result.get('error_message'):
                result['deployment_phase']['error'] = deployment_result['error_message']
            
            result['success'] = deployment_result.get('success', False)
            result['final_status'] = deployment_result.get('final_stack_status')
            
            return result
            
        except Exception as e:
            logger.exception(f"Error in fix_and_deploy: {e}")
            return {
                'success': False,
                'error': str(e),
                'stack_name': stack_name,
                'timestamp': datetime.utcnow().isoformat()
            }
    
    def _generate_comprehensive_fix_recommendations(
        self,
        template_analysis: Dict[str, Any],
        correlation: Dict[str, Any],
        base_analysis: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Generate comprehensive fix recommendations"""
        recommendations = []
        
        try:
            # High-priority template issues
            high_priority_issues = [
                issue for issue in template_analysis.get('issues', [])
                if issue.severity == 'HIGH'
            ]
            
            for issue in high_priority_issues:
                recommendations.append({
                    'priority': 'HIGH',
                    'category': 'Template Issue',
                    'issue': issue.description,
                    'fix_suggestion': issue.fix_suggestion,
                    'resource': issue.resource_id,
                    'automated_fix_available': True
                })
            
            # Security issues
            security_issues = template_analysis.get('security_issues', [])
            for security_issue in security_issues:
                recommendations.append({
                    'priority': 'HIGH',
                    'category': 'Security',
                    'issue': security_issue.get('description', ''),
                    'fix_suggestion': security_issue.get('fix_suggestion', ''),
                    'resource': security_issue.get('resource', ''),
                    'automated_fix_available': True
                })
            
            # Missing components
            missing_components = template_analysis.get('missing_components', [])
            for component in missing_components:
                recommendations.append({
                    'priority': 'MEDIUM',
                    'category': 'Missing Component',
                    'issue': component.get('description', ''),
                    'fix_suggestion': component.get('fix_suggestion', ''),
                    'automated_fix_available': True
                })
            
            # Correlated deployment failures
            correlated_issues = correlation.get('correlated_issues', [])
            for correlated_issue in correlated_issues:
                failure_analysis = correlated_issue.get('failure_analysis', {})
                if failure_analysis.get('template_related'):
                    recommendations.append({
                        'priority': 'HIGH',
                        'category': 'Deployment Failure',
                        'issue': f"Deployment failure: {failure_analysis.get('root_cause', '')}",
                        'fix_suggestion': '; '.join(correlated_issue.get('suggested_fixes', [])),
                        'resource': correlated_issue.get('resource_id', ''),
                        'automated_fix_available': failure_analysis.get('fix_confidence') in ['HIGH', 'MEDIUM']
                    })
            
            # Best practices violations
            best_practice_violations = template_analysis.get('best_practice_violations', [])
            for violation in best_practice_violations:
                recommendations.append({
                    'priority': 'LOW',
                    'category': 'Best Practice',
                    'issue': violation.get('description', ''),
                    'fix_suggestion': violation.get('fix_suggestion', ''),
                    'automated_fix_available': True
                })
            
            # Sort by priority
            priority_order = {'HIGH': 3, 'MEDIUM': 2, 'LOW': 1}
            recommendations.sort(key=lambda x: priority_order.get(x['priority'], 0), reverse=True)
            
            return recommendations
            
        except Exception as e:
            logger.exception(f"Error generating fix recommendations: {e}")
            return []
    
    def _create_autonomous_fix_plan(
        self,
        template: Dict[str, Any],
        template_analysis: Dict[str, Any],
        correlation: Dict[str, Any],
        stack_name: str
    ) -> Dict[str, Any]:
        """Create autonomous fix plan"""
        try:
            plan = {
                'feasible': True,
                'confidence': 'HIGH',
                'estimated_iterations': 1,
                'fix_phases': [],
                'risks': [],
                'prerequisites': []
            }
            
            # Analyze fix complexity
            total_issues = len(template_analysis.get('issues', []))
            high_confidence_fixes = sum(
                1 for issue in template_analysis.get('issues', [])
                if hasattr(issue, 'severity') and issue.severity == 'HIGH'
            )
            
            # Estimate iterations needed
            if total_issues == 0:
                plan['estimated_iterations'] = 1
                plan['confidence'] = 'HIGH'
            elif high_confidence_fixes / max(total_issues, 1) > 0.8:
                plan['estimated_iterations'] = 2
                plan['confidence'] = 'HIGH'
            elif high_confidence_fixes / max(total_issues, 1) > 0.5:
                plan['estimated_iterations'] = 3
                plan['confidence'] = 'MEDIUM'
            else:
                plan['estimated_iterations'] = 4
                plan['confidence'] = 'LOW'
            
            # Define fix phases
            if template_analysis.get('issues'):
                plan['fix_phases'].append({
                    'phase': 1,
                    'name': 'Template Issue Resolution',
                    'description': 'Fix template syntax and validation issues',
                    'estimated_duration': '2-5 minutes'
                })
            
            if template_analysis.get('security_issues'):
                plan['fix_phases'].append({
                    'phase': 2,
                    'name': 'Security Enhancement',
                    'description': 'Apply security best practices',
                    'estimated_duration': '1-3 minutes'
                })
            
            if template_analysis.get('missing_components'):
                plan['fix_phases'].append({
                    'phase': 3,
                    'name': 'Component Addition',
                    'description': 'Add missing required components',
                    'estimated_duration': '3-7 minutes'
                })
            
            plan['fix_phases'].append({
                'phase': len(plan['fix_phases']) + 1,
                'name': 'Iterative Deployment',
                'description': 'Deploy with automatic failure analysis and fixing',
                'estimated_duration': f"{plan['estimated_iterations'] * 5}-{plan['estimated_iterations'] * 10} minutes"
            })
            
            # Identify risks
            if correlation.get('correlated_issues'):
                plan['risks'].append('Previous deployment failures detected - may require multiple iterations')
            
            if template_analysis.get('dependencies'):
                circular_deps = any('circular' in str(dep).lower() for dep in template_analysis.get('dependencies', []))
                if circular_deps:
                    plan['risks'].append('Circular dependencies detected - may require manual intervention')
            
            # Prerequisites
            if any(issue.issue_type == 'PERMISSION_ERROR' for issue in template_analysis.get('issues', [])):
                plan['prerequisites'].append('Verify IAM permissions for deployment role')
            
            return plan
            
        except Exception as e:
            logger.exception(f"Error creating autonomous fix plan: {e}")
            return {
                'feasible': False,
                'error': str(e)
            }
    
    def _assess_deployment_readiness(
        self,
        template_analysis: Dict[str, Any],
        base_analysis: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Assess deployment readiness"""
        try:
            assessment = {
                'ready_for_deployment': True,
                'confidence': 'HIGH',
                'blocking_issues': [],
                'warnings': [],
                'recommendations': []
            }
            
            # Check for blocking issues
            high_severity_issues = [
                issue for issue in template_analysis.get('issues', [])
                if hasattr(issue, 'severity') and issue.severity == 'HIGH'
            ]
            
            if high_severity_issues:
                assessment['blocking_issues'].extend([
                    f"{issue.resource_id}: {issue.description}" 
                    for issue in high_severity_issues
                ])
            
            # Check for security issues
            security_issues = template_analysis.get('security_issues', [])
            if security_issues:
                assessment['warnings'].extend([
                    f"Security: {issue.get('description', '')}"
                    for issue in security_issues
                ])
            
            # Overall readiness assessment
            if assessment['blocking_issues']:
                assessment['ready_for_deployment'] = False
                assessment['confidence'] = 'LOW'
                assessment['recommendations'].append('Fix blocking issues before deployment')
            elif assessment['warnings']:
                assessment['confidence'] = 'MEDIUM'
                assessment['recommendations'].append('Consider addressing security warnings')
            else:
                assessment['recommendations'].append('Template appears ready for deployment')
            
            return assessment
            
        except Exception as e:
            logger.exception(f"Error assessing deployment readiness: {e}")
            return {
                'ready_for_deployment': False,
                'error': str(e)
            }
    
    def _create_comprehensive_summary(self, analysis: Dict[str, Any]) -> str:
        """Create comprehensive analysis summary"""
        try:
            summary_parts = []
            
            # Overall status
            stack_name = analysis.get('stack_name', 'Unknown')
            summary_parts.append(f"## Enhanced Analysis Summary for Stack: {stack_name}")
            
            # Template analysis summary
            template_analysis = analysis.get('template_analysis', {})
            if template_analysis:
                issues_count = len(template_analysis.get('issues', []))
                security_count = len(template_analysis.get('security_issues', []))
                missing_count = len(template_analysis.get('missing_components', []))
                
                summary_parts.append(f"### Template Analysis")
                summary_parts.append(f"- Issues found: {issues_count}")
                summary_parts.append(f"- Security concerns: {security_count}")
                summary_parts.append(f"- Missing components: {missing_count}")
            
            # Fix recommendations summary
            fix_recommendations = analysis.get('fix_recommendations', [])
            if fix_recommendations:
                high_priority = sum(1 for rec in fix_recommendations if rec.get('priority') == 'HIGH')
                automated_fixes = sum(1 for rec in fix_recommendations if rec.get('automated_fix_available'))
                
                summary_parts.append(f"### Fix Recommendations")
                summary_parts.append(f"- Total recommendations: {len(fix_recommendations)}")
                summary_parts.append(f"- High priority: {high_priority}")
                summary_parts.append(f"- Automated fixes available: {automated_fixes}")
            
            # Autonomous fix plan summary
            autonomous_plan = analysis.get('autonomous_fix_plan', {})
            if autonomous_plan.get('feasible'):
                summary_parts.append(f"### Autonomous Fix Plan")
                summary_parts.append(f"- Feasible: {autonomous_plan.get('feasible')}")
                summary_parts.append(f"- Confidence: {autonomous_plan.get('confidence')}")
                summary_parts.append(f"- Estimated iterations: {autonomous_plan.get('estimated_iterations')}")
            
            # Deployment readiness
            readiness = analysis.get('deployment_readiness', {})
            if readiness:
                summary_parts.append(f"### Deployment Readiness")
                summary_parts.append(f"- Ready: {readiness.get('ready_for_deployment')}")
                summary_parts.append(f"- Confidence: {readiness.get('confidence')}")
                if readiness.get('blocking_issues'):
                    summary_parts.append(f"- Blocking issues: {len(readiness['blocking_issues'])}")
            
            return '\n'.join(summary_parts)
            
        except Exception as e:
            logger.exception(f"Error creating comprehensive summary: {e}")
            return f"Error creating summary: {str(e)}"
